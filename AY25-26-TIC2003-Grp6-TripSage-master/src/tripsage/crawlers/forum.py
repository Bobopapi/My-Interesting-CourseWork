import os
import re
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class JapanGuideForumParser:
    """Parse Japan-Guide forum questions and extract location recommendations."""
    
    LOCATIONS = {
        "Tokyo", "Kyoto", "Osaka", "Sapporo", "Hiroshima", "Nagasaki", 
        "Nara", "Takayama", "Kanazawa", "Yokohama", "Kobe", "Shibuya",
        "Harajuku", "Shinjuku", "Akihabara", "Fukuoka", "Okinawa", "Hokkaido",
        "Honshu", "Kyushu", "Shikoku", "Mt. Fuji", "Kanto", "Kansai",
        "Nagano", "Osaka", "Kyoto-fu", "Shiga", "Hyogo", "Wakayama",
        "Okayama", "Hiroshima-ken", "Onomichi", "Naoshima", "Kamakura",
        "Mt Fuji", "Fuji", "Ginza", "Roppongi", "Ikebukuro", "Ueno",
        "Asakusa", "Senso-ji", "Meiji Shrine", "Universal", "Disneyland"
    }
    
    LOCAL_KEYWORDS = [
        "live in japan", "living in", "resident", "sensei", "japan-based",
        "been here", "years in", "years living", "came to japan", "moved to",
        "local here", "neighborhood", "my area", "where i live"
    ]

    def parse_forum_page(self, html_content: str, category: str = "travel") -> list[dict]:
        """Extract questions/discussions from forum category page HTML."""
        soup = BeautifulSoup(html_content, "lxml")
        posts = []
        
        # Find the main questions table (typically the 2nd large table on the page)
        tables = soup.find_all("table")
        if len(tables) < 2:
            logger.warning("Could not find questions table in forum page")
            return posts
        
        question_table = tables[1]  # Questions are in 2nd table
        rows = question_table.find_all("tr")
        
        # Skip header row (row 0)
        for row in rows[1:]:
            try:
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                
                # Cell 0: Title with link
                title_cell = cells[0]
                title_link = title_cell.find("a")
                
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                href = title_link.get("href", "")
                
                # Skip if title is empty or too short
                if not title or len(title) < 3:
                    continue
                
                # Extract post_id from href (URL format: /forum/quedetail.html?q=12345 or similar)
                post_id = self._extract_post_id(href)
                if not post_id:
                    # Use category + title as fallback ID
                    post_id = f"{category}_{len(posts)}_{title[:20].replace(' ', '_')}"
                
                # Cell 1: Reply/reaction count
                reply_count = 0
                try:
                    reply_text = cells[1].get_text(strip=True)
                    reply_count = int(reply_text) if reply_text.isdigit() else 0
                except (ValueError, IndexError):
                    reply_count = 0
                
                # Cell 2: Last updated time
                date_str = cells[2].get_text(strip=True) if len(cells) > 2 else "unknown"
                
                # Detect if poster is local (high reply count or local keywords in title)
                is_local = self._detect_local_poster(title, reply_count)
                
                # Extract locations mentioned in title
                locations = self._extract_locations(title)
                
                posts.append({
                    "post_id": post_id,
                    "title": title,
                    "url": f"https://www.japan-guide.com{href}" if href and href.startswith("/") else f"https://www.japan-guide.com/forum/{href}" if href else "",
                    "reply_count": reply_count,
                    "is_local": is_local,
                    "locations": ";".join(locations) if locations else "",
                    "category": category,
                    "last_updated": date_str
                })
            except Exception as e:
                logger.warning(f"Error parsing forum post: {e}")
                continue
        
        logger.info(f"Extracted {len(posts)} posts from forum page (category: {category})")
        return posts
    
    def _extract_post_id(self, href: str) -> str:
        """Extract post ID from href."""
        # Try to extract from URL parameters like ?q=12345
        match = re.search(r'[?&]q=(\d+)', href)
        if match:
            return match.group(1)
        
        # Try to extract from path like quedetail.html/123
        match = re.search(r'quedetail\.html[\?/](\d+)', href)
        if match:
            return match.group(1)
        
        return None
    
    def _detect_local_poster(self, title: str, reply_count: int) -> bool:
        """Heuristic to detect if poster is likely a local resident."""
        # Check for local keywords in title
        title_lower = title.lower()
        for keyword in self.LOCAL_KEYWORDS:
            if keyword in title_lower:
                return True
        
        # High reply count (10+) suggests active community member
        if reply_count >= 10:
            return True
        
        return False
    
    def _extract_locations(self, text: str) -> list[str]:
        """Extract Japan location mentions from text."""
        locations = []
        text_lower = text.lower()
        
        for loc in self.LOCATIONS:
            if loc.lower() in text_lower:
                locations.append(loc)
        
        return locations


class JapanGuideForumCrawler:
    """Crawl Japan-Guide forum for community insights and local recommendations."""
    
    FORUM_BASE_URL = "https://www.japan-guide.com/forum"
    
    # Forum categories with their type codes
    CATEGORIES = {
        "travel": 1,      # General travel questions
        "food": 2,        # Food and restaurants
        "shopping": 3     # Shopping questions
    }
    
    REQUEST_DELAY = 2  # seconds between requests
    
    def __init__(self, output_path: Path = None):
        self.parser = JapanGuideForumParser()
        self.output_path = output_path or Path("data/raw")
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.all_posts = []
        self.request_delay = float(os.getenv("REQUEST_DELAY", self.REQUEST_DELAY))
    
    @classmethod
    def from_env(cls):
        """Create crawler from environment settings."""
        return cls()
    
    def crawl_all_categories(self) -> int:
        """Crawl all forum categories."""
        total_posts = 0
        
        for category_name, category_code in self.CATEGORIES.items():
            posts = self._crawl_category(category_name, category_code)
            total_posts += len(posts)
            logger.info(f"Category '{category_name}': {len(posts)} posts")
        
        return total_posts
    
    def _crawl_category(self, category_name: str, category_code: int, max_pages: int = 3) -> list[dict]:
        """Crawl a specific forum category."""
        posts = []
        
        for page_num in range(max_pages):
            start_idx = page_num * 100  # 100 posts per page
            url = f"{self.FORUM_BASE_URL}/quedisplay.html?aTYPE={category_code}&aStart={start_idx}"
            
            logger.info(f"Crawling {category_name} page {page_num + 1}: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                page_posts = self.parser.parse_forum_page(response.text, category=category_name)
                posts.extend(page_posts)
                
                time.sleep(self.request_delay)
                
            except requests.RequestException as e:
                logger.error(f"Error fetching {url}: {e}")
                break
            except Exception as e:
                logger.error(f"Error parsing forum page: {e}")
                continue
        
        self.all_posts.extend(posts)
        return posts
    
    def save_forum_data(self, filename: str = "japan_guide_forum_posts.parquet") -> Path:
        """Save collected forum posts to parquet file."""
        if not self.all_posts:
            logger.warning("No forum posts to save")
            return None
        
        df = pd.DataFrame(self.all_posts)
        output_file = self.output_path / filename
        
        df.to_parquet(output_file, index=False)
        logger.info(f"Saved {len(df)} forum posts to {output_file}")
        
        return output_file


def main():
    crawler = JapanGuideForumCrawler.from_env()
    crawler.crawl_all_categories()
    crawler.save_forum_data()


if __name__ == "__main__":
    main()

