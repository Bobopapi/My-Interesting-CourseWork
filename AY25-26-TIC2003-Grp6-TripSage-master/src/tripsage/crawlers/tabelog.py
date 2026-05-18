import json
import os
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from tripsage.db.connection import DatabaseManager
from tripsage.db.repositories import TabelogRepository

load_dotenv()

DEFAULT_CITIES = {
    "Tokyo": "https://tabelog.com/en/tokyo/rstLst/",
}


class TabelogParser:
    def extract_detail_name(self, soup):
        # Primary: detailed page header name block.
        name_span = soup.select_one(".rdheader-rstname h2.display-name > span")
        if name_span:
            sub = name_span.select_one(".display-name__sub")
            if sub:
                sub.extract()
            name = name_span.get_text(" ", strip=True)
            if name:
                return name

        # Fallback: page title header.
        header_title = soup.select_one(".p-header__title h1")
        if header_title:
            name = header_title.get_text(" ", strip=True)
            if name:
                return name

        return None

    def extract_json_ld(self, soup):
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                continue

            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "Restaurant":
                        return item
                continue

            if data.get("@type") == "Restaurant":
                return data

        return None

    def parse_restaurant(self, html, url):
        soup = BeautifulSoup(html, "lxml")
        json_ld = self.extract_json_ld(soup)

        restaurant = {
            "name": None,
            "category": None,
            "price_range": None,
            "tabelog_rating": None,
            "review_count": None,
            "source_url": url,
        }

        # Prefer on-page display name from the detailed header section.
        restaurant["name"] = self.extract_detail_name(soup)

        if not json_ld:
            return restaurant

        if not restaurant["name"]:
            restaurant["name"] = json_ld.get("name")
        restaurant["price_range"] = json_ld.get("priceRange")

        cuisine = json_ld.get("servesCuisine")
        if cuisine:
            restaurant["category"] = cuisine.strip()

        aggregate_rating = json_ld.get("aggregateRating")
        if aggregate_rating:
            try:
                restaurant["tabelog_rating"] = float(aggregate_rating.get("ratingValue"))
            except (TypeError, ValueError):
                restaurant["tabelog_rating"] = None

            try:
                restaurant["review_count"] = int(aggregate_rating.get("ratingCount"))
            except (TypeError, ValueError):
                restaurant["review_count"] = None

        return restaurant

    def parse_review_page(self, html):
        soup = BeautifulSoup(html, "lxml")
        reviews = []

        for block in soup.select(".rvw-item.js-rvw-item-clickable-area"):
            # Tabelog review cards contain review id inside a data attribute
            review_id = None
            accordion_el = block.select_one("[data-accordion-key]")
            if accordion_el:
                key = accordion_el.get("data-accordion-key") or ""
                match = re.search(r"restaurant_review-id-(\d+)", key)
                if match:
                    review_id = match.group(1)

            if not review_id:
                # Fallback: search within the block HTML (covers cases where no
                # accordion element is present in the snapshot).
                match = re.search(r"restaurant_review-id-(\d+)", str(block))
                if match:
                    review_id = match.group(1)

            reviewer_el = block.select_one(".rvw-item__rvwr-name")
            reviewer_name = reviewer_el.get_text(strip=True) if reviewer_el else None

            review_text_el = block.select_one(".rvw-item__rvw-comment")
            review_text = review_text_el.get_text(" ", strip=True) if review_text_el else None

            rating = None
            rating_el = block.select_one(".c-rating-v3__val--strong, .c-rating__val")
            if rating_el:
                try:
                    rating = float(rating_el.get_text(strip=True))
                except ValueError:
                    rating = None

            review_date = None
            date_el = block.select_one(".rvw-item__date-inner span")
            if date_el:
                date_text = date_el.get_text(strip=True)
                # Example: "Visited on February, 2026"
                m = re.search(r"Visited on\s+([A-Za-z]+),\s*(\d{4})", date_text)
                if m:
                    month_name = m.group(1)
                    year = m.group(2)
                    try:
                        month_num = datetime.strptime(month_name, "%B").month
                        # Tabelog does not provide a day for these entries; use the first day.
                        review_date = f"{year}-{month_num:02d}-01"
                    except ValueError:
                        review_date = None

            reviews.append(
                {
                    "review_id": review_id,
                    "reviewer_name": reviewer_name,
                    "review_text": review_text,
                    "rating": rating,
                    "review_date": review_date,
                }
            )

        return reviews

    def extract_links(self, html):
        soup = BeautifulSoup(html, "lxml")
        links = []
        for anchor in soup.select(".list-rst__rst-name-target"):
            href = anchor.get("href")
            if href:
                links.append(href)
        return list(set(links))


class TabelogCrawler:
    def __init__(self, cities, max_restaurants, request_delay, max_review_pages, repository=None, parser=None, review_page_repository=None):
        self.cities = cities
        self.max_restaurants = max_restaurants
        self.request_delay = request_delay
        self.max_review_pages = max_review_pages
        self.repository = repository or TabelogRepository(DatabaseManager())
        self.parser = parser or TabelogParser()
        self.review_page_repository = review_page_repository
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    @classmethod
    def from_env(cls, repository=None, review_page_repository=None):
        return cls(
            cities=DEFAULT_CITIES,
            max_restaurants=int(os.getenv("MAX_RESULTS_PER_CITY", "5")),
            request_delay=int(os.getenv("REQUEST_DELAY", "2")),
            max_review_pages=int(os.getenv("MAX_REVIEW_PAGES", "3")),
            repository=repository,
            review_page_repository=review_page_repository,
        )

    def fetch_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            print(f"Error fetching {url}: {error}")
            return None

    def save_review_page(self, url, html, status="SUCCESS", error=None):
        if not self.review_page_repository:
            return

        self.review_page_repository.save_page(url, html, status=status, error=error)

    def parse_restaurant(self, url):
        html = self.fetch_page(url)
        if not html:
            return None, []

        self.repository.save_raw_restaurant_page(url, html)
        restaurant = self.parser.parse_restaurant(html, url)
        return restaurant, self.fetch_reviews(url)

    def fetch_reviews(self, base_url):
        reviews = []
        review_base = f"{base_url.rstrip('/')}/dtlrvwlst/"

        for page in range(1, self.max_review_pages + 1):
            # Tabelog paginates review list pages using the PG query parameter.
            review_url = review_base if page == 1 else f"{review_base}?PG={page}"
            print(f"      -> Review page {page}")

            html = self.fetch_page(review_url)
            if not html:
                self.save_review_page(review_url, None, status="FAILED", error="Fetch failed")
                break

            self.save_review_page(review_url, html, status="SUCCESS")
            page_reviews = self.parser.parse_review_page(html)
            if not page_reviews:
                break

            reviews.extend(page_reviews)

            time.sleep(self.request_delay)

        return reviews

    def extract_links(self, list_url):
        html = self.fetch_page(list_url)
        if not html:
            return []

        return self.parser.extract_links(html)

    def crawl_city(self, city, base_url):
        print(f"\n Crawling {city}")
        collected = 0
        page = 1

        while collected < self.max_restaurants:
            url = f"{base_url}{page}/"
            print(f"    Page {page}: {url}")

            links = self.extract_links(url)
            if not links:
                print("   WARN: No more restaurants found.")
                break

            for link in links:
                if collected >= self.max_restaurants:
                    break

                print(f"   -> {link}")
                restaurant, reviews = self.parse_restaurant(link)
                self.repository.save_restaurant(restaurant)
                self.repository.save_reviews(link, reviews)
                self.repository.save_core_reviews(link, reviews)

                collected += 1
                time.sleep(self.request_delay)

            page += 1

    def run(self):
        for city, url in self.cities.items():
            self.crawl_city(city, url)


def main():
    crawler = TabelogCrawler.from_env()
    crawler.run()
    print("\n Done crawling restaurants for major cities with raw HTML and reviews.")


if __name__ == "__main__":
    main()