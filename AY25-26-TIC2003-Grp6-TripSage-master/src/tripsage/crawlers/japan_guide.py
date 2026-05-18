import os
import re
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from tripsage.db.connection import DatabaseManager
from tripsage.db.repositories import JapanGuideRepository

load_dotenv()

DEFAULT_LIST_PAGE = "https://www.japan-guide.com/e/e2164.html"


class JapanGuideParser:
    def parse_attraction(self, html, url):
        soup = BeautifulSoup(html, "lxml")

        title_tag = soup.find("h1")
        name = title_tag.text.strip() if title_tag else None

        description = None
        main_content = soup.find("section", {"class": "page_section--main_content"})
        if main_content:
            first_paragraph = main_content.find("p")
            if first_paragraph:
                description = first_paragraph.text.strip()

        keywords = None
        meta_keywords = soup.find("meta", {"name": "keywords"})
        if meta_keywords and meta_keywords.has_attr("content"):
            keywords = meta_keywords["content"].strip()

        google_map_url = None
        iframe = (
            soup.find("iframe", {"id": "googlemap"})
            or soup.find("iframe", src=True)
            or soup.find("iframe", attrs={"data-src": True})
        )
        if iframe:
            google_map_url = iframe.get("data-src") or iframe.get("src")

        average_rating = None
        rating_div = soup.find("div", {"class": "rating_stars"})
        if rating_div:
            rating_num_span = rating_div.find_next_sibling("span", {"class": "place_details__number"})
            if rating_num_span:
                try:
                    average_rating = float(rating_num_span.text.strip())
                except ValueError:
                    average_rating = None

        return {
            "name": name,
            "description": description,
            "keywords": keywords,
            "google_map_url": google_map_url,
            "average_rating": average_rating,
            "source_url": url,
        }

    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, "lxml")
        links = []
        for anchor in soup.find_all("a", href=True):
            if anchor["href"].startswith("/e/"):
                links.append(f"{base_url}{anchor['href']}")
        return list(set(links))

    def extract_coordinates(self, google_map_url):
        if not google_map_url:
            return None

        match = re.search(r"center=([0-9\.-]+)%2C([0-9\.-]+)", google_map_url)
        if not match:
            return None

        return float(match.group(1)), float(match.group(2))


class LocationLookup:
    def __init__(self, request_delay, session=None):
        self.request_delay = request_delay
        self.session = session or requests.Session()

    def get_location(self, lat, lon):
        try:
            response = self.session.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "addressdetails": 1,
                },
                headers={"User-Agent": "TripSageCrawler/1.0 (contact: your_email@example.com)"},
                timeout=10,
            )
            response.raise_for_status()
            time.sleep(self.request_delay)
            data = response.json()
            address = data.get("address", {})

            return {
                "country": address.get("country"),
                "prefecture": address.get("state"),
                "city": address.get("city") or address.get("town") or address.get("village"),
                "district": address.get("suburb") or address.get("district"),
                "latitude": float(data.get("lat", lat)),
                "longitude": float(data.get("lon", lon)),
            }
        except (requests.RequestException, ValueError) as error:
            print(f"Error fetching location info: {error}")
            return {
                "country": None,
                "prefecture": None,
                "city": None,
                "district": None,
                "latitude": lat,
                "longitude": lon,
            }


class JapanGuideCrawler:
    def __init__(self, max_pages, request_delay, repository=None, parser=None, location_lookup=None, save_locations=False):
        self.max_pages = max_pages
        self.request_delay = request_delay
        self.base_url = "https://www.japan-guide.com"
        self.repository = repository or JapanGuideRepository(DatabaseManager())
        self.parser = parser or JapanGuideParser()
        self.location_lookup = location_lookup or LocationLookup(request_delay)
        self.save_locations = save_locations
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TripSage Academic Project Bot"})

    @classmethod
    def from_env(cls):
        request_delay = int(os.getenv("REQUEST_DELAY") or os.getenv("REQUEST_DELEY", "2"))
        return cls(
            max_pages=int(os.getenv("MAX_PAGE", "1")),
            request_delay=request_delay,
        )

    def fetch_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            print(f"Error fetching {url}: {error}")
            return None

    def build_location(self, attraction):
        coordinates = self.parser.extract_coordinates(attraction.get("google_map_url"))
        if not coordinates:
            return None

        lat, lon = coordinates
        location = self.location_lookup.get_location(lat, lon)
        location["name"] = attraction.get("name")
        return location

    def extract_links_from_list(self, list_url):
        html = self.fetch_page(list_url)
        if not html:
            return []

        return self.parser.extract_links(html, self.base_url)

    def crawl_list_page(self, list_url):
        links = self.extract_links_from_list(list_url)
        print(f"Found {len(links)} attraction links")

        for count, link in enumerate(links[: self.max_pages], start=1):
            print(f"Crawling ({count}/{self.max_pages}): {link}")
            html = self.fetch_page(link)
            if not html:
                continue

            attraction = self.parser.parse_attraction(html, link)
            self.repository.save_raw_page(link, html, page_type="attraction", title=attraction.get("name"))
            self.repository.save_attraction(attraction)

            if self.save_locations:
                location = self.build_location(attraction)
                if location:
                    self.repository.save_location(location)

            time.sleep(self.request_delay)


def main():
    crawler = JapanGuideCrawler.from_env()
    crawler.crawl_list_page(DEFAULT_LIST_PAGE)
    print("\n Done crawling attractions with raw HTML.")


if __name__ == "__main__":
    main()