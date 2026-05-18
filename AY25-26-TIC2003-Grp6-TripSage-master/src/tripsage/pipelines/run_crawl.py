import os

from tripsage.crawlers.japan_guide import DEFAULT_LIST_PAGE, JapanGuideCrawler
from tripsage.crawlers.forum import JapanGuideForumCrawler
from tripsage.crawlers.review import ReviewCrawlerApp


def run():
    # Crawl Japan-Guide attractions
    JapanGuideCrawler.from_env().crawl_list_page(DEFAULT_LIST_PAGE)
    
    # Crawl Japan-Guide forum discussions
    forum_crawler = JapanGuideForumCrawler.from_env()
    forum_crawler.crawl_all_categories()
    forum_crawler.save_forum_data()
    
    # Crawl Tabelog reviews
    ReviewCrawlerApp().run()


if __name__ == "__main__":
    run()
