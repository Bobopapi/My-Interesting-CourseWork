import re

from playwright.sync_api import Page, expect


def test_destination_details(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure we are on the destinations page and items are loaded
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Capture details of the first destination item before navigating
    first_item = page.locator('button:has-text("View Details")').nth(0)
    expect(first_item).to_be_visible()

    # Get the item's name from the card
    item_card = first_item.locator('xpath=ancestor::div[3]')
    item_name = item_card.locator('p').nth(0).text_content().strip()

    # Get category from badge
    category_badge = item_card.locator('text=Food').or_(item_card.locator('text=Attraction'))
    item_category = category_badge.text_content().strip()

    # Get location text
    location_text = item_card.locator('p').nth(1).text_content().strip()
    city, country = location_text.split(', ')

    # Get reviews count
    reviews_text = item_card.locator('p').nth(2).text_content().strip()
    reviews_match = re.search(r'Reviews: (\d+)', reviews_text)
    assert reviews_match is not None, f"Could not parse reviews count from: {reviews_text}"
    item_reviews_count = int(reviews_match.group(1))

    # Click the "View Details" button
    first_item.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Verify the details match
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


def test_destination_details_liked(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure we are on the destinations page and items are loaded
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Like the first destination item by clicking the heart icon
    liked_icons = page.locator('.lucide.lucide-heart')
    expect(liked_icons.nth(0)).to_be_visible()
    liked_icons.nth(0).click()
    page.wait_for_timeout(300)

    # Click the "View Details" button on the first item
    first_item = page.locator('button:has-text("View Details")').nth(0)
    first_item.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Verify that the liked button shows "Unlike" since we liked it
    liked_button = page.locator('button').filter(has_text='Unlike')
    expect(liked_button).to_be_visible()


def test_destination_details_unlike(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure we are on the destinations page and items are loaded
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Like the first destination item by clicking the heart icon
    liked_icons = page.locator('.lucide.lucide-heart')
    expect(liked_icons.nth(0)).to_be_visible()
    liked_icons.nth(0).click()
    page.wait_for_timeout(300)

    # Click the "View Details" button on the first item
    first_item = page.locator('button:has-text("View Details")').nth(0)
    first_item.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Click the "Unlike" button to unlike the item
    unlike_button = page.locator('button').filter(has_text='Unlike')
    unlike_button.click()
    page.wait_for_timeout(300)

    # Verify that the button now shows "Like" (since it's unliked)
    liked_button = page.locator('button').filter(has_text='Like')
    expect(liked_button).to_be_visible()

    # Click the "Back" button to return to destinations
    back_button = page.locator('button').filter(has_text='Back')
    back_button.click()
    page.wait_for_load_state('networkidle')

    # Verify we are back on the destinations page
    expect(page).to_have_url(base_url + '/')

    # Click the "Like" filter to check if the item is no longer liked
    page.click('button:has-text("Liked")')
    page.wait_for_timeout(300)

    # Verify that no items are displayed (since we unliked the only item)
    view_details_buttons = page.locator('button:has-text("View Details")')
    button_count = view_details_buttons.count()
    assert button_count == 0, "Expected no liked items after unliking"


def test_destination_details_visit(page: Page, base_url: str):
    page.goto(base_url)
    page.wait_for_load_state('networkidle')

    # Ensure we are on the destinations page and items are loaded
    page.click('button:has-text("All")')
    page.wait_for_timeout(300)

    # Click the "View Details" button on the first item
    first_item = page.locator('button:has-text("View Details")').nth(0)
    first_item.click()
    page.wait_for_load_state('networkidle')

    # Verify we are on the details page
    expect(page).to_have_url(re.compile(r'/details/\d+'))

    # Click the "Visited" button to mark as visited
    visited_button = page.locator('button').filter(has_text='Visited')
    visited_button.click()
    page.wait_for_timeout(300)

    # Verify that the button now shows "Unvisit" (since it's visited)
    unvisit_button = page.locator('button').filter(has_text='Unvisit')
    expect(unvisit_button).to_be_visible()

    # Click the "Back" button to return to destinations
    back_button = page.locator('button').filter(has_text='Back')
    back_button.click()
    page.wait_for_load_state('networkidle')

    # Verify we are back on the destinations page
    expect(page).to_have_url(base_url + '/')

    # Verify that the first item now shows the "Visited" badge
    visited_badges = page.locator('text=Visited')
    expect(visited_badges.nth(0)).to_be_visible()