CREATE OR REPLACE FUNCTION raw.pull_bronze_japan_guide_pages()
RETURNS TABLE (
    url TEXT,
    page_type VARCHAR(50),
    title TEXT,
    raw_html TEXT,
    scraped_at TIMESTAMP,
    status VARCHAR(20),
    error_message TEXT
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
    SELECT
        url,
        page_type,
        title,
        raw_html,
        scraped_at,
        status,
        error_message
    FROM raw.japan_guide_pages;
$$;

CREATE OR REPLACE FUNCTION raw.pull_bronze_tabelog_restaurants()
RETURNS TABLE (
    url TEXT,
    raw_html TEXT,
    scraped_at TIMESTAMP,
    status VARCHAR(20),
    error_message TEXT
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
    SELECT
        url,
        raw_html,
        scraped_at,
        status,
        error_message
    FROM raw.tabelog_restaurants;
$$;

CREATE OR REPLACE FUNCTION raw.pull_bronze_tabelog_reviews()
RETURNS TABLE (
    restaurant_url TEXT,
    review_id TEXT,
    reviewer_name TEXT,
    review_text TEXT,
    rating NUMERIC(2,1),
    review_date DATE,
    scraped_at TIMESTAMP
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
    SELECT
        restaurant_url,
        review_id,
        reviewer_name,
        review_text,
        rating,
        review_date,
        scraped_at
    FROM raw.tabelog_reviews;
$$;

GRANT EXECUTE ON FUNCTION raw.pull_bronze_japan_guide_pages() TO tripsage_app;
GRANT EXECUTE ON FUNCTION raw.pull_bronze_tabelog_restaurants() TO tripsage_app;
GRANT EXECUTE ON FUNCTION raw.pull_bronze_tabelog_reviews() TO tripsage_app;