CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.japan_guide_pages (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    page_type VARCHAR(50),
    title TEXT,
    raw_html TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'SUCCESS',
    error_message TEXT,
    CONSTRAINT unique_japan_guide_url UNIQUE (url)
);

CREATE TABLE IF NOT EXISTS raw.tabelog_restaurants (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    raw_html TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'SUCCESS',
    error_message TEXT,
    CONSTRAINT unique_tabelog_restaurant_url UNIQUE (url)
);

CREATE TABLE IF NOT EXISTS raw.tabelog_reviews (
    id BIGSERIAL PRIMARY KEY,
    restaurant_url TEXT NOT NULL,
    review_id TEXT NOT NULL,
    reviewer_name TEXT,
    review_text TEXT,
    rating NUMERIC(2,1),
    review_date DATE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_restaurant_review UNIQUE (restaurant_url, review_id)
);

CREATE TABLE IF NOT EXISTS raw.tabelog_review_pages (
    id BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    raw_html TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    error_message TEXT
);
