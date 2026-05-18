import re

from playwright.sync_api import Page, expect


HIGHLIGHTS_RATING_PATTERN = re.compile(r"Highlights: ([0-9]+\.[0-9]{2}) \| Trending: ([0-9]+\.[0-9]{2})")


def _parse_ratings(line: str) -> tuple[float, float]:
    match = HIGHLIGHTS_RATING_PATTERN.search(line)
    assert match is not None, f"Rating line did not match expected format: {line}"
    return float(match.group(1)), float(match.group(2))


def _sorted_descending(values: list[float]) -> bool:
    return values == sorted(values, reverse=True)


def test_sort_by_highlights(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure the Highlights sort button is selected and the page is rendered.
    page.click('text=Highlights')
    page.wait_for_timeout(300)

    lines = page.locator('text=Highlights:')
    count = lines.count()
    assert count >= 2, "Expected at least two destination items for sorting verification"
    expect(lines.nth(0)).to_be_visible()

    highlight_values = []
    for index in range(count):
        text = lines.nth(index).text_content() or ""
        highlights, _ = _parse_ratings(text)
        highlight_values.append(highlights)

    assert _sorted_descending(highlight_values), (
        f"Destination items are not sorted by highlights descending: {highlight_values}"
    )


def test_sort_by_trending_now(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    page.click('text=Trending Now')
    page.wait_for_timeout(300)

    lines = page.locator('text=Highlights:')
    count = lines.count()
    assert count >= 2, "Expected at least two destination items for sorting verification"
    expect(lines.nth(0)).to_be_visible()

    trending_values = []
    for index in range(count):
        text = lines.nth(index).text_content() or ""
        _, trending = _parse_ratings(text)
        trending_values.append(trending)

    assert _sorted_descending(trending_values), (
        f"Destination items are not sorted by trending descending: {trending_values}"
    )


def test_search_by_country(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Get the initial list of items to find a valid country to search for.
    location_texts = page.locator('text=/^[^,]+, [^,]+$/').all()
    assert len(location_texts) >= 1, "Expected at least one destination item on the page"
    
    first_location = location_texts[0].text_content() or ""
    country = first_location.split(",")[-1].strip()
    
    # Fill in the country search field and submit.
    page.fill('input[name="country"]', country)
    page.click('button:has-text("Search")')
    page.wait_for_timeout(500)

    # Verify all displayed items contain the searched country.
    location_texts_after = page.locator('text=/^[^,]+, [^,]+$/').all()
    assert len(location_texts_after) >= 1, "Expected at least one result after country search"

    for location_text in location_texts_after:
        location = location_text.text_content() or ""
        displayed_country = location.split(",")[-1].strip()
        assert country.lower() in displayed_country.lower(), (
            f"Expected country '{country}' in location '{location}'"
        )


def test_search_by_city(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Get the initial list of items to find a valid city to search for.
    location_texts = page.locator('text=/^[^,]+, [^,]+$/').all()
    assert len(location_texts) >= 1, "Expected at least one destination item on the page"
    
    first_location = location_texts[0].text_content() or ""
    city = first_location.split(",")[0].strip()
    
    # Fill in the city search field and submit.
    page.fill('input[name="city"]', city)
    page.click('button:has-text("Search")')
    page.wait_for_timeout(500)

    # Verify all displayed items contain the searched city.
    location_texts_after = page.locator('text=/^[^,]+, [^,]+$/').all()
    assert len(location_texts_after) >= 1, "Expected at least one result after city search"

    for location_text in location_texts_after:
        location = location_text.text_content() or ""
        displayed_city = location.split(",")[0].strip()
        assert city.lower() in displayed_city.lower(), (
            f"Expected city '{city}' in location '{location}'"
        )


def test_filter_all_destinations(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Click the "All" filter button.
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Verify that destination items are displayed by checking for "View Details" buttons.
    view_details_buttons = page.locator('button:has-text("View Details")')
    button_count = view_details_buttons.count()
    assert button_count >= 1, "Expected at least one destination item when viewing all"


def test_filter_attractions(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Click the "Attractions" filter button.
    page.click('button:has-text("Attractions")')
    page.wait_for_timeout(300)

    # Verify that all displayed items are attractions.
    badges = page.locator('text=Attraction')
    badge_count = badges.count()
    assert badge_count >= 1, "Expected at least one attraction item when filtering by Attractions"


def test_filter_food(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Click the "Food" filter button.
    page.click('button:has-text("Food")')
    page.wait_for_timeout(300)

    # Verify that all displayed items are food.
    badges = page.locator('text=Food')
    badge_count = badges.count()
    assert badge_count >= 1, "Expected at least one food item when filtering by Food"


def test_filter_liked(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Start by showing all items.
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Find and like the first destination item by clicking the first heart icon.
    # The heart icon is part of each destination card.
    liked_icons = page.locator('.lucide.lucide-heart')
    expect(liked_icons.nth(0)).to_be_visible()
    if liked_icons.count() >= 1:
        liked_icons.nth(0).click()
        page.wait_for_timeout(300)

    # Click the "Like" filter button.
    page.click('button:has-text("Like")')
    page.wait_for_timeout(300)

    # Verify that only liked items are displayed by checking for "View Details" buttons.
    view_details_buttons = page.locator('button:has-text("View Details")')
    button_count = view_details_buttons.count()
    assert button_count >= 1, "Expected at least one liked item when filtering by Liked"
