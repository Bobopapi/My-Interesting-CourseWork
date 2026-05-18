class JapanGuideRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def save_raw_page(self, url, html, page_type="attraction", title=None, status="SUCCESS", error_message=None):
        self.db_manager.execute(
            """
            CALL raw.ingest_japan_guide_page(%s, %s, %s, %s, %s, %s);
            """,
            (url, page_type, title, html, status, error_message),
        )

    def save_attraction(self, attraction):
        # Silver entities are now built in parquet by a separate Polars job.
        return

    def save_location(self, location):
        # Silver entities are now built in parquet by a separate Polars job.
        return


class TabelogRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def save_raw_restaurant_page(self, url, html, status="SUCCESS", error=None):
        self.db_manager.execute(
            """
            CALL raw.ingest_tabelog_restaurant(%s, %s, %s, %s);
            """,
            (url, html, status, error),
        )

    def save_restaurant(self, restaurant):
        # Silver entities are now built in parquet by a separate Polars job.
        return

    def save_reviews(self, restaurant_url, reviews):
        rows = []
        for review in reviews:
            if not review.get("review_id"):
                continue
            rows.append(
                (
                    restaurant_url,
                    review.get("review_id"),
                    review.get("reviewer_name"),
                    review.get("review_text"),
                    review.get("rating"),
                    review.get("review_date"),
                )
            )

        self.db_manager.execute_many(
            """
            CALL raw.ingest_tabelog_review(%s, %s, %s, %s, %s, %s);
            """,
            rows,
        )

    def get_restaurant_id_by_source_url(self, source_url):
        return None

    def save_core_reviews(self, restaurant_url, reviews, language="en"):
        # Silver entities are now built in parquet by a separate Polars job.
        return


class TabelogReviewPageRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def save_page(self, url, html, status="SUCCESS", error=None):
        self.db_manager.execute(
            """
            CALL raw.ingest_tabelog_review_page(%s, %s, %s, %s);
            """,
            (url, html, status, error),
        )