from tripsage.crawlers.tabelog import TabelogCrawler
from tripsage.db.connection import DatabaseManager
from tripsage.db.repositories import TabelogRepository, TabelogReviewPageRepository


class ReviewCrawlerApp:
    def __init__(self, crawler=None):
        if crawler is None:
            db_manager = DatabaseManager()
            crawler = TabelogCrawler.from_env(
                repository=TabelogRepository(db_manager),
                review_page_repository=TabelogReviewPageRepository(db_manager),
            )

        self.crawler = crawler

    def run(self):
        self.crawler.run()


def main():
    app = ReviewCrawlerApp()
    app.run()
    print("\n Done crawling restaurants for major cities with raw HTML and reviews.")


if __name__ == "__main__":
    main()