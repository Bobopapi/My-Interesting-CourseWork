from datetime import datetime, timezone
from pathlib import Path
import sys
import uuid

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tripsage.db.connection import DatabaseManager


class SilverLayerBuilder:
    def __init__(self, db_manager=None, output_dir="data/core"):
        self.db_manager = db_manager or DatabaseManager()
        self.output_dir = Path(output_dir)

    def _query_to_polars(self, query):
        with self.db_manager.connection() as conn:
            rows = pl.read_database(query=query, connection=conn)
        return rows

    def pull_bronze(self):
        attractions = self._query_to_polars("SELECT * FROM raw.pull_bronze_japan_guide_pages();")
        restaurants = self._query_to_polars("SELECT * FROM raw.pull_bronze_tabelog_restaurants();")
        reviews = self._query_to_polars("SELECT * FROM raw.pull_bronze_tabelog_reviews();")
        return attractions, restaurants, reviews

    def load_forum_data(self):
        """Load forum posts from parquet file if available."""
        raw_dir = self.output_dir.parent / "raw"
        forum_file = raw_dir / "japan_guide_forum_posts.parquet"
        
        if forum_file.exists():
            try:
                return pl.read_parquet(forum_file)
            except Exception as e:
                print(f"Note: Could not load forum data: {e}")
        
        return pl.DataFrame()

    def _extract_first(self, text_col, pattern):
        return pl.col(text_col).cast(pl.Utf8).str.extract(pattern, 1)

    def _append_metadata(self, frame, source_key_expr, source_sys):
        batch_id = str(uuid.uuid4())
        batch_timestamp = datetime.now(timezone.utc).isoformat()
        return frame.with_columns(
            [
                pl.lit(batch_id).alias("_batch_id"),
                source_key_expr.alias("_source_key"),
                pl.lit(source_sys).alias("_source_sys"),
                pl.lit(batch_timestamp).alias("_batch_timestamp"),
            ]
        )

    def transform_attractions(self, bronze_attractions):
        if bronze_attractions.is_empty():
            return bronze_attractions

        frame = bronze_attractions.with_columns(
            [
                pl.col("url").cast(pl.Utf8),
                pl.col("title").cast(pl.Utf8),
                pl.col("page_type").cast(pl.Utf8),
                pl.col("raw_html").cast(pl.Utf8),
                self._extract_first("raw_html", r'(?is)<meta[^>]*name="keywords"[^>]*content="([^"]+)"').alias("keywords"),
                pl.coalesce(
                    [
                        self._extract_first("raw_html", r'(?is)<iframe[^>]*id="googlemap"[^>]*data-src="([^"]+)"'),
                        self._extract_first("raw_html", r'(?is)<iframe[^>]*id="googlemap"[^>]*src="([^"]+)"'),
                    ]
                ).alias("google_map_url"),
            ]
        ).with_columns(
            [
                pl.coalesce([pl.col("title"), pl.col("url")]).str.strip_chars().alias("name"),
                pl.col("page_type").fill_null("attraction").alias("category"),
            ]
        ).select(
            [
                pl.col("url").alias("source_url"),
                pl.col("name"),
                pl.col("category"),
                pl.col("keywords"),
                pl.col("google_map_url"),
                pl.col("scraped_at"),
                pl.col("status"),
                pl.col("error_message"),
            ]
        )

        frame = frame.filter(pl.col("name").is_not_null() & (pl.col("name") != ""))
        frame = frame.unique(subset=["source_url"], keep="last")
        return self._append_metadata(frame, pl.col("source_url"), "japan_guide")

    def transform_restaurants(self, bronze_restaurants, bronze_reviews):
        if bronze_restaurants.is_empty():
            return bronze_restaurants

        extracted_name = pl.coalesce(
            [
                # Example target: <div class="rdheader-rstname"><h2 class="display-name"><span>...</span></h2>
                self._extract_first(
                    "raw_html",
                    r'(?is)<div[^>]*class="[^"]*rdheader-rstname[^"]*"[^>]*>.*?<h2[^>]*class="[^"]*display-name[^"]*"[^>]*>\s*<span>\s*([^<]+)'
                ),
                # Fallback to JSON-LD name if available.
                self._extract_first(
                    "raw_html",
                    r'(?is)"@type"\s*:\s*"Restaurant".*?"name"\s*:\s*"([^"]+)"'
                ),
            ]
        ).str.strip_chars()

        review_agg = (
            bronze_reviews.with_columns(pl.col("restaurant_url").cast(pl.Utf8))
            .group_by("restaurant_url")
            .agg(
                [
                    pl.col("rating").mean().round(1).alias("tabelog_rating"),
                    pl.col("review_id").n_unique().alias("review_count"),
                ]
            )
        )

        frame = (
            bronze_restaurants.with_columns(
                [
                    pl.col("url").cast(pl.Utf8),
                    pl.col("raw_html").cast(pl.Utf8),
                ]
            )
            .join(review_agg, left_on="url", right_on="restaurant_url", how="left")
            .with_columns(
                [
                    pl.col("url").alias("source_url"),
                    pl.coalesce([extracted_name, pl.col("url")]).alias("name"),
                    pl.lit("Restaurant").alias("category"),
                ]
            )
            .select(
                [
                    "source_url",
                    "name",
                    "category",
                    "tabelog_rating",
                    "review_count",
                    "scraped_at",
                    "status",
                    "error_message",
                ]
            )
            .unique(subset=["source_url"], keep="last")
        )

        return self._append_metadata(frame, pl.col("source_url"), "tabelog")

    def transform_reviews(self, bronze_reviews):
        if bronze_reviews.is_empty():
            return bronze_reviews

        frame = bronze_reviews.with_columns(
            [
                pl.col("restaurant_url").cast(pl.Utf8),
                pl.col("review_id").cast(pl.Utf8),
                pl.col("review_text").str.replace_all(r"\\s+", " ").str.strip_chars().alias("review_text"),
                pl.col("reviewer_name").str.replace_all(r"\\s+", " ").str.strip_chars().alias("reviewer_name"),
            ]
        ).filter(
            pl.col("review_id").is_not_null()
            & (pl.col("review_id") != "")
            & pl.col("review_text").is_not_null()
            & (pl.col("review_text") != "")
        )

        frame = frame.with_columns(
            (
                pl.col("restaurant_url")
                + pl.lit("|")
                + pl.col("review_id")
            ).alias("source_review_key")
        ).select(
            [
                pl.col("source_review_key"),
                pl.col("restaurant_url"),
                pl.col("review_id"),
                pl.col("reviewer_name"),
                pl.col("review_text"),
                pl.col("rating"),
                pl.col("review_date"),
                pl.col("scraped_at"),
            ]
        )

        frame = frame.unique(subset=["source_review_key"], keep="last")
        return self._append_metadata(frame, pl.col("source_review_key"), "tabelog")

    def transform_forum_posts(self, forum_posts):
        """Transform Japan-Guide forum posts into review-like records with local indicator."""
        if forum_posts.is_empty():
            return forum_posts

        frame = forum_posts.with_columns(
            [
                pl.col("post_id").cast(pl.Utf8),
                pl.col("title").cast(pl.Utf8).str.strip_chars(),
                pl.col("url").cast(pl.Utf8).str.strip_chars(),
                pl.col("is_local").cast(pl.Boolean),
            ]
        ).filter(
            pl.col("post_id").is_not_null()
            & (pl.col("post_id") != "")
            & pl.col("title").is_not_null()
            & (pl.col("title") != "")
        )

        # Create source review key from URL and ID
        frame = frame.with_columns(
            (
                pl.col("url")
                + pl.lit("|")
                + pl.col("post_id")
            ).alias("source_review_key")
        ).select(
            [
                pl.col("source_review_key"),
                pl.col("url").alias("location_url"),
                pl.col("post_id"),
                pl.lit("community").alias("reviewer_name"),  # Forum posts are community insights
                pl.col("title").alias("review_text"),  # Title is the main content
                pl.col("last_updated").alias("review_date"),
                pl.col("is_local"),
                pl.col("locations").alias("location_tags"),
                pl.col("category"),
            ]
        )

        frame = frame.unique(subset=["source_review_key"], keep="last")
        return self._append_metadata(frame, pl.col("source_review_key"), "japan_guide_forum")

    def upsert_parquet(self, file_name, source_key_col, new_frame):
        output_path = self.output_dir / file_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        def _ensure_source_key(frame: pl.DataFrame) -> pl.DataFrame:
            if source_key_col in frame.columns:
                return frame

            # Recover natural keys from legacy parquet shapes so upsert still merges.
            fallback_keys = ["source_review_key", "source_url", "url", "post_id"]
            for key_col in fallback_keys:
                if key_col in frame.columns:
                    return frame.with_columns(pl.col(key_col).cast(pl.Utf8).alias(source_key_col))
            return frame

        new_frame = _ensure_source_key(new_frame)

        if output_path.exists():
            existing = _ensure_source_key(pl.read_parquet(output_path))
            if source_key_col in existing.columns and source_key_col in new_frame.columns:
                merged = pl.concat([existing, new_frame], how="diagonal_relaxed")
            else:
                # Replace legacy parquet shape that does not carry silver metadata.
                merged = new_frame
        else:
            merged = new_frame

        if not merged.is_empty():
            merged = merged.unique(subset=[source_key_col], keep="last")
        merged.write_parquet(output_path)
        print(f"Upserted {len(new_frame)} rows -> {output_path}")

    def run(self):
        bronze_attractions, bronze_restaurants, bronze_reviews = self.pull_bronze()

        silver_attractions = self.transform_attractions(bronze_attractions)
        silver_restaurants = self.transform_restaurants(bronze_restaurants, bronze_reviews)
        silver_reviews = self.transform_reviews(bronze_reviews)

        self.upsert_parquet("attractions.parquet", "_source_key", silver_attractions)
        self.upsert_parquet("restaurants.parquet", "_source_key", silver_restaurants)
        self.upsert_parquet("reviews.parquet", "_source_key", silver_reviews)

        # Also process forum posts if available
        forum_posts = self.load_forum_data()
        if not forum_posts.is_empty():
            silver_forum = self.transform_forum_posts(forum_posts)
            self.upsert_parquet("forum_reviews.parquet", "_source_key", silver_forum)


def main():
    builder = SilverLayerBuilder()
    builder.run()


if __name__ == "__main__":
    main()
