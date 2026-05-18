import re

from playwright.sync_api import Page, expect


def test_travel_log_visited_item(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure we are on the destinations page and items are loaded
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Capture details of the first destination item before navigating
    first_item_button = page.locator('button:has-text("View Details")').nth(0)
    item_card = first_item_button.locator('xpath=ancestor::div[3]')
    item_name = item_card.locator('p').nth(0).text_content().strip()
    category_badge = item_card.locator('text=Food').or_(item_card.locator('text=Attraction'))
    item_category = category_badge.text_content().strip()
    location_text = item_card.locator('p').nth(1).text_content().strip()
    city, country = location_text.split(', ')
    reviews_text = item_card.locator('p').nth(2).text_content().strip()
    reviews_match = re.search(r'Reviews: (\d+)', reviews_text)
    assert reviews_match is not None, f"Could not parse reviews count from: {reviews_text}"
    item_reviews_count = int(reviews_match.group(1))

    # Click the "View Details" button on the first item
    first_item_button.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Click the "Visited" button to mark as visited
    visited_button = page.locator('button').filter(has_text='Visited')
    visited_button.click()
    page.wait_for_timeout(300)

    # Navigate to the travel log page
    page.goto(f"{base_url}/travel-log")
    page.wait_for_load_state('networkidle')

    # Verify we are on the travel log page
    expect(page).to_have_url(re.compile(r'/travel-log'))

    # Verify that the visited item appears in the travel log
    # Check for the item name
    expect(page.locator(f'text={item_name}')).to_be_visible()

    # Check for the category badge
    expect(page.locator(f'text={item_category}')).to_be_visible()

    # Check for the location
    expect(page.locator(f'text={city}, {country}')).to_be_visible()

    # Check for the reviews count
    expect(page.locator(f'text=Reviews: {item_reviews_count}')).to_be_visible()

    # Check for the "Open Details" button
    open_details_buttons = page.locator('button:has-text("Open Details")')
    assert open_details_buttons.count() > 0

    # Click the "Open Details" button
    open_details_buttons.first.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Verify the details match the captured item
    # Name
    heading = page.locator('h1').nth(0)
    expect(heading).to_have_text(item_name)

    # Category badge
    category_badge_detail = page.locator('text=Food').or_(page.locator('text=Attraction'))
    expect(category_badge_detail).to_have_text(item_category)

    # Location
    location_detail = page.locator(f'text={city}, {country}')
    expect(location_detail).to_be_visible()

    # Reviews count
    reviews_detail = page.locator(f'text=Reviews: {item_reviews_count}')
    expect(reviews_detail).to_be_visible()


def test_travel_log_unvisit_removes_item(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure we are on the destinations page and items are loaded
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Capture details of the first destination item before navigating
    first_item_button = page.locator('button:has-text("View Details")').nth(0)
    item_card = first_item_button.locator('xpath=ancestor::div[3]')
    item_name = item_card.locator('p').nth(0).text_content().strip()

    # Click the "View Details" button on the first item
    first_item_button.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Click the "Visited" button to mark as visited
    visited_button = page.locator('button').filter(has_text='Visited')
    visited_button.click()
    page.wait_for_timeout(300)

    # Navigate to the travel log page
    page.goto(f"{base_url}/travel-log")
    page.wait_for_load_state('networkidle')

    # Verify we are on the travel log page
    expect(page).to_have_url(re.compile(r'/travel-log'))

    # Verify that the visited item appears in the travel log
    expect(page.locator(f'text={item_name}')).to_be_visible()

    # Go back to the details page (assuming we can navigate back or go directly)
    page.goto(base_url)  # Go back to destinations
    page.wait_for_load_state('networkidle')
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)
    first_item_button = page.locator('button:has-text("View Details")').nth(0)
    first_item_button.click()
    page.wait_for_load_state('networkidle')

    # Click the "Unvisit" button
    unvisit_button = page.locator('button').filter(has_text='Unvisit')
    unvisit_button.click()
    page.wait_for_timeout(300)

    # Navigate back to the travel log page
    page.goto(f"{base_url}/travel-log")
    page.wait_for_load_state('networkidle')

    # Verify that the item no longer appears in the travel log
    expect(page.locator(f'text={item_name}')).not_to_be_visible()