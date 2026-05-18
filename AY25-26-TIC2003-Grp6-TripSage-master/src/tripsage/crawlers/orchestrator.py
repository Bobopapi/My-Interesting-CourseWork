"""Orchestrator for running all data collection crawlers."""
import os
from pathlib import Path

from tripsage.crawlers.japan_guide import DEFAULT_LIST_PAGE, JapanGuideCrawler
from tripsage.crawlers.japan_guide_ratings import JapanGuideRatingsCrawler
from tripsage.crawlers.forum import JapanGuideForumCrawler
from tripsage.crawlers.review import ReviewCrawlerApp


def run_japan_guide_attractions():
    """Crawl Japan-Guide attractions and extract ratings."""
    print("=" * 60)
    print("CRAWLING JAPAN-GUIDE ATTRACTIONS")
    print("=" * 60)
    
    crawler = JapanGuideCrawler.from_env()
    
    # First pass: crawl attraction pages (populates raw pages)
    crawler.crawl_list_page(DEFAULT_LIST_PAGE)
    
    # Note: ratings extraction would be integrated into the main crawler
    # For now, it's set up as a separate module for future enhancement
    print("(Ratings extraction to be integrated in next phase)")


def run_japan_guide_forum():
    """Crawl Japan-Guide forum for local discussions."""
    print("\n" + "=" * 60)
    print("CRAWLING JAPAN-GUIDE FORUM")
    print("=" * 60)
    
    crawler = JapanGuideForumCrawler.from_env()
    crawler.crawl_all_categories()
    crawler.save_forum_data()


def run_tabelog_reviews():
    """Crawl Tabelog restaurant reviews."""
    print("\n" + "=" * 60)
    print("CRAWLING TABELOG RESTAURANTS & REVIEWS")
    print("=" * 60)
    
    app = ReviewCrawlerApp()
    app.run()


def run():
    """Execute all crawlers."""
    run_japan_guide_attractions()
    run_japan_guide_forum()
    run_tabelog_reviews()


if __name__ == "__main__":
    run()
