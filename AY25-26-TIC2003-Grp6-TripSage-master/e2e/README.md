# TripSage Playwright Automation Tests

This directory contains end-to-end (E2E) tests for the TripSage application using Python Playwright with pytest.

## Test Files

The following test suites are available:

- **test_auth.py** - Authentication tests (login, registration, logout)
- **test_dashboard.py** - Dashboard page tests
- **test_destinations.py** - Destinations browser tests
- **test_travel_log.py** - Travel log functionality tests
- **test_settings.py** - User settings and preferences tests
- **test_example.py** - Example template tests
- **test_system.py** - General application tests

## Prerequisites

Before running the tests, ensure you have:

1. **Python 3.12+** installed
2. **Virtual environment activated**
3. **Playwright** installed via `requirements.txt`
4. **TripSage application running** on `http://localhost:3000`

## Installation

Install the required Python dependencies:

```bash
python -m pip install -r requirements.txt
python -m playwright install
```

## Running Tests

### Run all tests
```bash
pytest e2e
```

### Run a specific suite
```bash
pytest e2e/test_auth.py
pytest e2e/test_dashboard.py
pytest e2e/test_destinations.py
pytest e2e/test_travel_log.py
pytest e2e/test_settings.py
pytest e2e/test_system.py
pytest e2e/test_example.py
```

## Configuration

The pytest configuration is in `pytest.ini`:

- **Test directory**: `e2e`
- **Python file pattern**: `test_*.py`
- **Quiet mode**: `-q`

### Base URL
The base URL is configured in `e2e/conftest.py` using the `BASE_URL` environment variable.
Default:

```bash
http://localhost:3000
```

## Test Structure

Each test file uses pytest and Python Playwright fixtures:

```python
from playwright.sync_api import Page, expect

def test_example(page: Page, base_url: str):
    page.goto(f"{base_url}/")
    expect(page).to_have_title("TripSage")
```

## Best Practices

1. Use semantic locators:
   ```python
   page.locator('button:has-text("Login")')
   page.locator('input[name="email"]')
   ```

2. Wait for elements properly:
   ```python
   expect(element).to_be_visible(timeout=5000)
   page.wait_for_load_state('networkidle')
   ```

3. Keep tests independent and reusable.
4. Use fixtures for shared setup.
5. Keep test names descriptive.

## Debugging

### Run a single test
```bash
pytest e2e/test_auth.py -q
```

### Run with verbose output
```bash
pytest e2e -vv
```

### Capture traces
Playwright Python traces can be enabled by adding `trace='on-first-retry'` in your Playwright configuration or using the `playwright` CLI if necessary.

## CI/CD Integration

Use pytest directly in your CI pipeline:

```yaml
- name: Run E2E tests
  run: pytest e2e
```

If you need browser binaries installed on CI, add:

```bash
python -m playwright install
```

## Extending Tests

1. Create a new file under `e2e/` named `test_<feature>.py`.
2. Use pytest and the Playwright `page` fixture.
3. Add descriptive test names and keep them small.

## Troubleshooting

### Tests timeout
- Increase assertion timeout in the test.
- Use `page.wait_for_load_state('networkidle')`.

### Element not found
- Verify selectors match the app.
- Confirm the app is running on `BASE_URL`.

### Application not running
- Start TripSage before running tests.
- Check `http://localhost:3000`.

## Resources

- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [pytest Docs](https://docs.pytest.org/)

---

**Last Updated:** April 2026
