import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


class JapanGuideRatingsParser:
    """Extract star ratings and user feedback from Japan-Guide attraction pages."""

    def parse_ratings(self, html, url):
        """Extract all ratings from the page.
        
        Returns:
            list of dicts with keys: rating, reviewer_name, review_text, review_date, source_url
        """
        soup = BeautifulSoup(html, "lxml")
        ratings = []

        # Find all rating blocks - they appear in the page with user comments
        rating_containers = soup.find_all("div", {"class": re.compile(r"rating_stars")})

        for container in rating_containers:
            # Check if this is actual user rating (has tooltip with rating text)
            tooltip = container.get("data-tooltip-label", "")
            if not tooltip:
                continue

            # Extract star count from span elements
            star_spans = container.find_all("span", {"class": re.compile(r"rating_stars__star")})
            if not star_spans:
                continue

            rating_value = self._extract_rating_from_stars(star_spans)
            if rating_value is None:
                continue

            # Try to find associated comment and reviewer info nearby
            parent = container.parent
            reviewer_name = None
            review_text = None
            review_date = None

            # Look for reviewer info in nearby siblings or parent containers
            if parent:
                # Look for reviewer name (often in a span or div near the rating)
                name_elem = parent.find("span", {"class": re.compile(r"reviewer|author|user")})
                if not name_elem:
                    name_elem = parent.find("strong")
                reviewer_name = name_elem.get_text(strip=True) if name_elem else None

                # Look for review text (often in a paragraph following the rating)
                text_elem = parent.find("p") or parent.find("div", {"class": re.compile(r"comment|text|review")})
                if text_elem:
                    review_text = text_elem.get_text(" ", strip=True)[:500]  # Limit text

                # Look for date (often near reviewer info)
                date_elem = parent.find("span", {"class": re.compile(r"date|time")})
                if not date_elem:
                    date_elem = parent.find_next("span")
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    review_date = self._parse_date(date_text)

            ratings.append(
                {
                    "rating": rating_value,
                    "reviewer_name": reviewer_name or "Anonymous",
                    "review_text": review_text or tooltip,
                    "review_date": review_date,
                    "source_url": url,
                    "is_local": False,  # Will be determined by other heuristics if needed
                }
            )

        return ratings

    def _extract_rating_from_stars(self, star_spans):
        """Extract rating from star span elements.
        
        Counts active stars or extracts from data-rate attributes.
        """
        active_count = 0
        total_stars = 5

        for star in star_spans:
            if "is-active" in star.get("class", []):
                active_count += 1

        if active_count > 0:
            return active_count

        # Fallback: look for data-rate attribute on first active star
        for star in star_spans:
            if "is-active" in star.get("class", []):
                rate_val = star.get("data-rate")
                if rate_val:
                    try:
                        return float(rate_val)
                    except ValueError:
                        pass

        return None

    def _parse_date(self, date_text):
        """Parse date string to YYYY-MM-DD format."""
        if not date_text:
            return None

        try:
            # Try common patterns
            if "ago" in date_text.lower():
                # Relative date - use today
                return datetime.now(timezone.utc).date().isoformat()

            # Try parsing with various formats
            for fmt in ["%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%b %d, %Y"]:
                try:
                    return datetime.strptime(date_text, fmt).date().isoformat()
                except ValueError:
                    continue

            return None
        except Exception:
            return None


class JapanGuideRatingsCrawler:
    """Crawl and store star ratings from Japan-Guide attraction pages."""

    def __init__(self, request_delay=2, output_dir="data/raw"):
        self.request_delay = request_delay
        self.output_dir = Path(output_dir)
        self.parser = JapanGuideRatingsParser()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TripSage Academic Project Bot"})
        self.ratings_data = []

    @classmethod
    def from_env(cls):
        request_delay = int(os.getenv("REQUEST_DELAY", "2"))
        return cls(request_delay=request_delay)

    def fetch_page(self, url):
        """Fetch page with error handling."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            print(f"Error fetching {url}: {error}")
            return None

    def crawl_attraction(self, url):
        """Crawl ratings from a single attraction page."""
        html = self.fetch_page(url)
        if not html:
            return 0

        ratings = self.parser.parse_ratings(html, url)
        self.ratings_data.extend(ratings)
        return len(ratings)

    def crawl_attractions(self, attraction_urls):
        """Crawl ratings from multiple attraction URLs."""
        for idx, url in enumerate(attraction_urls, start=1):
            print(f"Crawling ratings ({idx}/{len(attraction_urls)}): {url}")
            count = self.crawl_attraction(url)
            print(f"  Found {count} ratings")
            time.sleep(self.request_delay)

    def save_ratings(self, filename="japan_guide_ratings.parquet"):
        """Save collected ratings to parquet file."""
        if not self.ratings_data:
            print("No ratings data to save")
            return

        df = pd.DataFrame(self.ratings_data)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename

        df.to_parquet(output_path, index=False)
        print(f"Saved {len(df)} ratings to {output_path}")


def main():
    crawler = JapanGuideRatingsCrawler.from_env()
    # This would be called with actual attraction URLs from the main crawler
    # For now, it's a standalone module
    pass


if __name__ == "__main__":
    main()
