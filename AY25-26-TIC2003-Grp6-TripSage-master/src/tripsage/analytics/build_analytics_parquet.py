from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np
# we will keep this simple with a small set of positive and negative words for sentiment analysis without using nltk library

POSITIVE_WORDS = {
    "amazing",
    "awesome",
    "best",
    "clean",
    "cozy",
    "delicious",
    "excellent",
    "fantastic",
    "friendly",
    "fresh",
    "great",
    "helpful",
    "highly",
    "impressive",
    "kind",
    "love",
    "lovely",
    "perfect",
    "pleasant",
    "recommend",
    "satisfying",
    "stunning",
    "superb",
    "tasty",
    "wonderful",
}

NEGATIVE_WORDS = {
    "awful",
    "bad",
    "bland",
    "cold",
    "crowded",
    "dirty",
    "disappointing",
    "expensive",
    "hate",
    "horrible",
    "limited",
    "mediocre",
    "overpriced",
    "poor",
    "rude",
    "salty",
    "slow",
    "small",
    "terrible",
    "tough",
    "unfriendly",
    "waste",
    "weak",
    "worst",
}

STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "but",
    "by",
    "can",
    "did",
    "do",
    "for",
    "from",
    "had",
    "has",
    "have",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "just",
    "more",
    "my",
    "no",
    "not",
    "of",
    "on",
    "or",
    "our",
    "so",
    "than",
    "that",
    "the",
    "their",
    "them",
    "there",
    "these",
    "they",
    "this",
    "to",
    "too",
    "very",
    "was",
    "we",
    "were",
    "with",
    "you",
    "your",
}

PREFECTURES = {
    "tokyo",
    "osaka",
    "kyoto",
    "hokkaido",
    "okinawa",
    "fukuoka",
    "hyogo",
    "nara",
    "aichi",
    "kanagawa",
    "chiba",
    "saitama",
    "shizuoka",
    "nagano",
    "hiroshima",
    "miyagi",
}


class AnalyticsLayerBuilder:
    def __init__(
        self,
        core_dir: str = "data/core",
        analytics_output_dir: str = "data/analytics",
        presentation_output_dir: str = "data/presentation",
    ):
        self.core_dir = Path(core_dir)
        self.analytics_output_dir = Path(analytics_output_dir)
        self.presentation_output_dir = Path(presentation_output_dir)

    def _read_parquet(self, file_name: str) -> pd.DataFrame:
        file_path = self.core_dir / file_name
        if not file_path.exists():
            return pd.DataFrame()
        return pd.read_parquet(file_path)

    def load_core(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        attractions = self._read_parquet("attractions.parquet")
        restaurants = self._read_parquet("restaurants.parquet")
        reviews = self._read_parquet("reviews.parquet")
        locations = self._read_parquet("locations.parquet")
        return attractions, restaurants, reviews, locations

    def load_additional_sources(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load forum reviews and other local source data."""
        forum_reviews = self._read_parquet("forum_reviews.parquet")
        return forum_reviews, pd.DataFrame()  # Empty second item for future expansion

    def reconcile_reviews(self, reviews: pd.DataFrame) -> pd.DataFrame:
        if reviews.empty:
            return reviews

        frame = reviews.copy()
        frame["review_text"] = frame["review_text"].fillna("").astype(str)
        frame["review_text"] = frame["review_text"].str.replace(r"\s+", " ", regex=True).str.strip()
        frame["restaurant_url"] = frame["restaurant_url"].fillna("").astype(str).str.strip()
        frame["source_review_key"] = frame["source_review_key"].fillna("").astype(str).str.strip()
        frame["rating"] = pd.to_numeric(frame.get("rating"), errors="coerce")
        frame["review_date"] = pd.to_datetime(frame.get("review_date"), errors="coerce")

        frame = frame[
            (frame["review_text"] != "")
            & (frame["restaurant_url"] != "")
            & (frame["source_review_key"] != "")
        ]
        frame = frame.drop_duplicates(subset=["source_review_key"], keep="last")
        return frame

    def _tokenize(self, text: str) -> list[str]:
        if not isinstance(text, str) or not text:
            return []
        return re.findall(r"[a-zA-Z][a-zA-Z']+", text.lower())

    def _sentiment_score(self, text: str, rating: float | None) -> float:
        tokens = self._tokenize(text)
        if tokens:
            positive = sum(1 for token in tokens if token in POSITIVE_WORDS)
            negative = sum(1 for token in tokens if token in NEGATIVE_WORDS)
            lexical_score = (positive - negative) / max(len(tokens), 1)
        else:
            lexical_score = 0.0

        if pd.notna(rating):
            rating_score = max(min((float(rating) - 3.0) / 2.0, 1.0), -1.0)
            blended = lexical_score * 0.7 + rating_score * 0.3
        else:
            blended = lexical_score
        return float(max(min(blended, 1.0), -1.0))

    def _score_to_label(self, score: float) -> str:
        if score >= 0.2:
            return "Positive"
        if score <= -0.2:
            return "Negative"
        return "Neutral"

    def build_review_sentiment(self, reviews: pd.DataFrame) -> pd.DataFrame:
        if reviews.empty:
            return pd.DataFrame(columns=["source_review_key", "sentiment_score", "sentiment_label"])

        frame = reviews[["source_review_key", "restaurant_url", "rating", "review_text"]].copy()
        frame["sentiment_score"] = frame.apply(
            lambda row: self._sentiment_score(row["review_text"], row["rating"]),
            axis=1,
        )
        frame["sentiment_label"] = frame["sentiment_score"].apply(self._score_to_label)
        frame["sentiment_score"] = frame["sentiment_score"].round(3)
        return frame

    def build_review_keywords(self, reviews: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
        rows: list[dict[str, object]] = []
        if reviews.empty:
            return pd.DataFrame(columns=["source_review_key", "keyword", "frequency", "rank"])

        for review_key, text in reviews[["source_review_key", "review_text"]].itertuples(index=False):
            tokens = [
                token
                for token in self._tokenize(text)
                if token not in STOPWORDS and len(token) >= 3 and not token.isdigit()
            ]
            if not tokens:
                continue

            frequencies = pd.Series(tokens).value_counts().head(top_k)
            for rank, (keyword, frequency) in enumerate(frequencies.items(), start=1):
                rows.append(
                    {
                        "source_review_key": review_key,
                        "keyword": keyword,
                        "frequency": int(frequency),
                        "rank": rank,
                    }
                )

        return pd.DataFrame(rows)

    def _extract_prefecture(self, source_url: str, keywords: str = "") -> str:
        if isinstance(source_url, str):
            match = re.search(r"/en/([a-z-]+)/", source_url.lower())
            if match and match.group(1) in PREFECTURES:
                return match.group(1).title()

        if isinstance(keywords, str):
            lower_keywords = keywords.lower()
            for prefecture in PREFECTURES:
                if prefecture in lower_keywords:
                    return prefecture.title()

        return "Unknown"

    def _series_or_default(self, frame: pd.DataFrame, column: str, default_value) -> pd.Series:
        if column in frame.columns:
            return frame[column]
        return pd.Series([default_value] * len(frame), index=frame.index)

    def build_entities(
        self,
        attractions: pd.DataFrame,
        restaurants: pd.DataFrame,
        locations: pd.DataFrame,
    ) -> pd.DataFrame:
        rows: list[pd.DataFrame] = []

        if not attractions.empty:
            attractions_frame = attractions.copy()
            attractions_frame["entity_type"] = "attraction"
            attractions_frame["entity_key"] = attractions_frame["source_url"].astype(str)
            attractions_frame["rating"] = pd.to_numeric(
                self._series_or_default(attractions_frame, "average_rating", None), errors="coerce"
            )
            attractions_frame["review_count"] = pd.to_numeric(
                self._series_or_default(attractions_frame, "review_count", 0), errors="coerce"
            ).fillna(0).astype(int)
            attractions_frame["category"] = self._series_or_default(
                attractions_frame, "category", "Attraction"
            ).fillna("Attraction")
            attractions_frame["prefecture"] = attractions_frame.apply(
                lambda row: self._extract_prefecture(row.get("source_url"), row.get("keywords", "")),
                axis=1,
            )
            attractions_frame["city"] = "Unknown"
            attractions_frame["location_name"] = attractions_frame["prefecture"]
            rows.append(
                attractions_frame[
                    [
                        "entity_type",
                        "entity_key",
                        "name",
                        "category",
                        "prefecture",
                        "city",
                        "location_name",
                        "rating",
                        "review_count",
                        "source_url",
                    ]
                ]
            )

        if not restaurants.empty:
            restaurants_frame = restaurants.copy()
            restaurants_frame["entity_type"] = "food"
            restaurants_frame["entity_key"] = restaurants_frame["source_url"].astype(str)
            restaurants_frame["rating"] = pd.to_numeric(
                self._series_or_default(restaurants_frame, "tabelog_rating", None), errors="coerce"
            )
            restaurants_frame["review_count"] = pd.to_numeric(
                self._series_or_default(restaurants_frame, "review_count", 0), errors="coerce"
            ).fillna(0).astype(int)
            restaurants_frame["category"] = self._series_or_default(
                restaurants_frame, "category", "Restaurant"
            ).fillna("Restaurant")
            restaurants_frame["prefecture"] = restaurants_frame["source_url"].map(self._extract_prefecture)
            restaurants_frame["city"] = "Unknown"
            restaurants_frame["location_name"] = restaurants_frame["prefecture"]
            rows.append(
                restaurants_frame[
                    [
                        "entity_type",
                        "entity_key",
                        "name",
                        "category",
                        "prefecture",
                        "city",
                        "location_name",
                        "rating",
                        "review_count",
                        "source_url",
                    ]
                ]
            )

        if not rows:
            return pd.DataFrame(
                columns=[
                    "entity_type",
                    "entity_key",
                    "name",
                    "category",
                    "prefecture",
                    "city",
                    "location_name",
                    "rating",
                    "review_count",
                    "source_url",
                ]
            )

        entities = pd.concat(rows, ignore_index=True)
        entities["name"] = entities["name"].fillna("Unknown")
        entities = entities.drop_duplicates(subset=["entity_type", "entity_key"], keep="last")
        return entities

    def build_entity_metrics(self, sentiment: pd.DataFrame) -> pd.DataFrame:
        if sentiment.empty:
            return pd.DataFrame(columns=["entity_type", "entity_key", "avg_sentiment", "positive_ratio", "total_reviews"])

        metrics = (
            sentiment.assign(entity_type="food", entity_key=sentiment["restaurant_url"].astype(str))
            .groupby(["entity_type", "entity_key"], as_index=False)
            .agg(
                avg_sentiment=("sentiment_score", "mean"),
                positive_ratio=("sentiment_label", lambda s: (s == "Positive").mean() * 100),
                total_reviews=("source_review_key", "count"),
            )
        )
        metrics["avg_sentiment"] = metrics["avg_sentiment"].round(3)
        metrics["positive_ratio"] = metrics["positive_ratio"].round(2)
        return metrics

    def build_gold_entities(self, entities: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
        if entities.empty:
            return entities

        merged = entities.merge(metrics, on=["entity_type", "entity_key"], how="left")

        def sentiment_label(row: pd.Series) -> str:
            avg = row.get("avg_sentiment")
            rating = row.get("rating")
            if pd.notna(avg):
                if avg >= 0.2:
                    return "Positive"
                if avg <= -0.2:
                    return "Negative"
                return "Neutral"

            if pd.isna(rating):
                return "Unknown"
            if rating >= 4.0:
                return "Positive"
            if rating >= 3.0:
                return "Neutral"
            return "Negative"

        merged["sentiment_label"] = merged.apply(sentiment_label, axis=1)
        merged["recommendation_score"] = (
            ((merged["rating"].fillna(0) / 5.0) * 0.70)
            + (merged["review_count"].fillna(0).clip(upper=500) / 500.0) * 0.30
        ) * 100.0
        merged["recommendation_score"] = merged["recommendation_score"].round(1)

        return merged.sort_values(["recommendation_score", "rating", "review_count"], ascending=[False, False, False])

    def build_gold_reviews(self, reviews: pd.DataFrame) -> pd.DataFrame:
        if reviews.empty:
            return reviews

        frame = reviews.copy()
        frame["entity_type"] = "food"
        frame["entity_key"] = frame["restaurant_url"].astype(str)
        
        # Calculate recency metrics
        today = pd.Timestamp("2026-04-12")  # Use fixed date for consistency
        frame["review_date"] = pd.to_datetime(frame["review_date"], errors="coerce")
        frame["days_ago"] = (today - frame["review_date"]).dt.days
        frame["days_ago"] = frame["days_ago"].fillna(-1).astype(int)  # -1 for missing dates
        
        # Calculate recency score (0-100): newer reviews score higher
        # Using logarithmic decay: newer reviews (0 days) = 100, older reviews decay
        def calculate_recency_score(days):
            if days < 0:
                return 0.0  # Missing date
            if days == 0:
                return 100.0
            # Logarithmic decay: half-life of 30 days
            return float(100.0 * (0.5 ** (days / 30.0)))
        
        frame["recency_score"] = frame["days_ago"].apply(calculate_recency_score).round(1)
        
        return frame[
            [
                "source_review_key",
                "entity_type",
                "entity_key",
                "review_date",
                "days_ago",
                "recency_score",
                "rating",
                "review_text",
                "restaurant_url",
            ]
        ].rename(columns={"restaurant_url": "source_url"})

    def build_prefecture_summary(self, gold_entities: pd.DataFrame) -> pd.DataFrame:
        if gold_entities.empty:
            return pd.DataFrame(columns=["prefecture", "entity_type", "entity_count", "avg_rating", "total_reviews", "avg_recommendation_score"])

        summary = (
            gold_entities.groupby(["prefecture", "entity_type"], as_index=False)
            .agg(
                entity_count=("entity_key", "count"),
                avg_rating=("rating", "mean"),
                total_reviews=("review_count", "sum"),
                avg_recommendation_score=("recommendation_score", "mean"),
            )
            .sort_values(["entity_count", "avg_recommendation_score"], ascending=[False, False])
        )
        summary["avg_rating"] = summary["avg_rating"].round(2)
        summary["avg_recommendation_score"] = summary["avg_recommendation_score"].round(2)
        return summary

    def build_category_summary(self, gold_entities: pd.DataFrame) -> pd.DataFrame:
        if gold_entities.empty:
            return pd.DataFrame(columns=["entity_type", "category", "entity_count", "avg_rating", "total_reviews", "avg_recommendation_score"])

        summary = (
            gold_entities.groupby(["entity_type", "category"], as_index=False)
            .agg(
                entity_count=("entity_key", "count"),
                avg_rating=("rating", "mean"),
                total_reviews=("review_count", "sum"),
                avg_recommendation_score=("recommendation_score", "mean"),
            )
            .sort_values(["entity_count", "avg_recommendation_score"], ascending=[False, False])
        )
        summary["avg_rating"] = summary["avg_rating"].round(2)
        summary["avg_recommendation_score"] = summary["avg_recommendation_score"].round(2)
        return summary

    def build_monthly_review_activity(self, gold_reviews: pd.DataFrame) -> pd.DataFrame:
        if gold_reviews.empty or "review_date" not in gold_reviews.columns:
            return pd.DataFrame(columns=["month_start", "entity_type", "review_count", "avg_rating"])

        frame = gold_reviews.dropna(subset=["review_date"]).copy()
        if frame.empty:
            return pd.DataFrame(columns=["month_start", "entity_type", "review_count", "avg_rating"])

        frame["month_start"] = pd.to_datetime(frame["review_date"]).dt.to_period("M").dt.to_timestamp()
        summary = (
            frame.groupby(["month_start", "entity_type"], as_index=False)
            .agg(review_count=("source_review_key", "count"), avg_rating=("rating", "mean"))
            .sort_values(["month_start", "entity_type"])
        )
        summary["avg_rating"] = summary["avg_rating"].round(2)
        return summary

    def build_keywords_summary(
        self,
        review_keywords: pd.DataFrame,
        review_sentiment: pd.DataFrame,
        reviews: pd.DataFrame,
        entities: pd.DataFrame,
    ) -> pd.DataFrame:
        """Build gold-layer keyword summary with sentiment and entity context for wordcloud visualization."""
        if review_keywords.empty or review_sentiment.empty:
            return pd.DataFrame(
                columns=[
                    "keyword",
                    "frequency",
                    "positive_count",
                    "neutral_count",
                    "negative_count",
                    "sentiment_distribution",
                    "entity_type",
                    "category",
                    "avg_rating",
                ]
            )

        # Join keywords with sentiment
        keywords_with_sentiment = review_keywords.merge(
            review_sentiment[["source_review_key", "sentiment_label", "rating"]],
            on="source_review_key",
            how="left",
        )

        # Join with reviews to get entity info
        keywords_with_sentiment = keywords_with_sentiment.merge(
            reviews[["source_review_key", "restaurant_url"]],
            on="source_review_key",
            how="left",
        )

        # Join with entities to get entity type and category
        keywords_with_sentiment = keywords_with_sentiment.merge(
            entities[["entity_key", "entity_type", "category", "rating"]].rename(
                columns={"entity_key": "restaurant_url", "rating": "entity_rating"}
            ),
            on="restaurant_url",
            how="left",
        )

        # Use entity_rating if available, else use review rating
        keywords_with_sentiment["rating"] = keywords_with_sentiment["rating"].fillna(
            keywords_with_sentiment["entity_rating"]
        )

        # Aggregate by keyword, entity_type, and category
        summary = (
            keywords_with_sentiment.groupby(
                ["keyword", "entity_type", "category"], as_index=False
            )
            .agg(
                frequency=("keyword", "count"),
                positive_count=("sentiment_label", lambda s: (s == "Positive").sum()),
                neutral_count=("sentiment_label", lambda s: (s == "Neutral").sum()),
                negative_count=("sentiment_label", lambda s: (s == "Negative").sum()),
                avg_rating=("rating", "mean"),
            )
        )

        # Calculate sentiment distribution (0-1, where 1 = all positive, 0 = all negative)
        summary["sentiment_distribution"] = (
            (summary["positive_count"] - summary["negative_count"]) / summary["frequency"]
        ).round(3)

        # Sort by frequency (descending)
        summary = summary.sort_values("frequency", ascending=False)

        return summary

    def build_local_insights(self, forum_reviews: pd.DataFrame) -> pd.DataFrame:
        """Build gold-layer insights from local (forum) reviews.
        
        Highlights location recommendations and discussions from community members
        who are identified as locals or established members. Includes source URLs
        for direct access to forum posts.
        """
        if forum_reviews.empty:
            return pd.DataFrame(
                columns=[
                    "location",
                    "source",
                    "mention_count",
                    "sample_posts",
                    "source_url",
                ]
            )

        frame = forum_reviews.copy()
        frame["is_local"] = frame.get("is_local", False)
        
        # Filter to local sources (high engagement = 10+ replies)
        local_frame = frame[frame["is_local"] == True] if "is_local" in frame.columns else frame.head(0)
        
        if local_frame.empty:
            return pd.DataFrame(columns=["location", "source", "mention_count", "sample_posts", "source_url"])

        # Parse location tags and capture source URLs
        results = []
        for idx, row in local_frame.iterrows():
            tags = row.get("location_tags", "") or ""
            if pd.isna(tags) or tags == "":
                continue
            
            location_list = str(tags).split(";")
            for location in location_list:
                location = location.strip()
                if location:
                    results.append(
                        {
                            "location": location,
                            "source": row.get("category", "travel"),
                            "mention_count": 1,
                            "post_id": row.get("post_id"),
                            "review_text": row.get("review_text", ""),
                            "source_url": row.get("location_url", ""),  # Forum post URL
                        }
                    )

        if not results:
            return pd.DataFrame(columns=["location", "source", "mention_count", "sample_posts", "source_url"])

        summary_df = pd.DataFrame(results)
        summary_df = (
            summary_df.groupby(["location", "source"], as_index=False)
            .agg(
                mention_count=("mention_count", "sum"),
                sample_posts=("review_text", lambda x: " | ".join(x.values[:2])),
                source_url=("source_url", "first"),  # Take first URL for the location+source group
            )
            .sort_values("mention_count", ascending=False)
        )

        return summary_df

    def _write_parquet(self, frame: pd.DataFrame, file_name: str, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / file_name
        frame.to_parquet(output_path, index=False)
        print(f"Wrote {len(frame)} rows -> {output_path}")

    def _write_analytics(self, frame: pd.DataFrame, file_name: str) -> None:
        self._write_parquet(frame, file_name, self.analytics_output_dir)

    def _write_presentation(self, frame: pd.DataFrame, file_name: str) -> None:
        self._write_parquet(frame, file_name, self.presentation_output_dir)

    def run(self) -> None:
        attractions, restaurants, reviews, locations = self.load_core()
        forum_reviews, _ = self.load_additional_sources()
        
        reviews = self.reconcile_reviews(reviews)

        # Build analytics layer outputs
        review_sentiment = self.build_review_sentiment(reviews)
        review_keywords = self.build_review_keywords(reviews)
        entity_metrics = self.build_entity_metrics(review_sentiment)

        # Write analytics layer
        self._write_analytics(review_sentiment, "review_sentiment.parquet")
        self._write_analytics(review_keywords, "review_keywords.parquet")
        self._write_analytics(entity_metrics, "entity_metrics.parquet")

        # Build presentation (gold) layer outputs
        entities = self.build_entities(attractions, restaurants, locations)
        gold_entities = self.build_gold_entities(entities, entity_metrics)
        gold_reviews = self.build_gold_reviews(reviews)
        prefecture_summary = self.build_prefecture_summary(gold_entities)
        category_summary = self.build_category_summary(gold_entities)
        monthly_activity = self.build_monthly_review_activity(gold_reviews)
        keywords_summary = self.build_keywords_summary(
            review_keywords, review_sentiment, reviews, entities
        )

        # Build local insights if forum data available
        local_insights = self.build_local_insights(forum_reviews)

        # Write presentation (gold) layer
        self._write_presentation(gold_entities, "viz_entities.parquet")
        self._write_presentation(gold_reviews, "viz_reviews.parquet")
        self._write_presentation(prefecture_summary, "viz_prefecture_summary.parquet")
        self._write_presentation(category_summary, "viz_category_summary.parquet")
        self._write_presentation(monthly_activity, "viz_monthly_review_activity.parquet")
        self._write_presentation(keywords_summary, "viz_keywords_summary.parquet")
        
        if not local_insights.empty:
            self._write_presentation(local_insights, "viz_local_insights.parquet")


def main() -> None:
    AnalyticsLayerBuilder().run()


if __name__ == "__main__":
    main()
