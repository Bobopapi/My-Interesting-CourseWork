DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'tripsage_app'
    ) THEN
        CREATE ROLE tripsage_app LOGIN PASSWORD 'tripsage_app_test';
    ELSE
        ALTER ROLE tripsage_app LOGIN PASSWORD 'tripsage_app_test';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE "TripSage" TO tripsage_app;
GRANT USAGE ON SCHEMA raw TO tripsage_app;

CREATE OR REPLACE PROCEDURE raw.ingest_japan_guide_page(
    p_url TEXT,
    p_page_type VARCHAR(50),
    p_title TEXT,
    p_raw_html TEXT,
    p_status VARCHAR(20),
    p_error_message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
BEGIN
    INSERT INTO raw.japan_guide_pages (
        url,
        page_type,
        title,
        raw_html,
        status,
        error_message,
        scraped_at
    )
    VALUES (
        p_url,
        p_page_type,
        p_title,
        p_raw_html,
        COALESCE(p_status, 'SUCCESS'),
        p_error_message,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (url) DO UPDATE
    SET page_type = EXCLUDED.page_type,
        title = EXCLUDED.title,
        raw_html = EXCLUDED.raw_html,
        status = EXCLUDED.status,
        error_message = EXCLUDED.error_message,
        scraped_at = EXCLUDED.scraped_at;
END;
$$;

CREATE OR REPLACE PROCEDURE raw.ingest_tabelog_restaurant(
    p_url TEXT,
    p_raw_html TEXT,
    p_status VARCHAR(20),
    p_error_message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
BEGIN
    INSERT INTO raw.tabelog_restaurants (
        url,
        raw_html,
        status,
        error_message,
        scraped_at
    )
    VALUES (
        p_url,
        p_raw_html,
        COALESCE(p_status, 'SUCCESS'),
        p_error_message,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (url) DO UPDATE
    SET raw_html = EXCLUDED.raw_html,
        status = EXCLUDED.status,
        error_message = EXCLUDED.error_message,
        scraped_at = EXCLUDED.scraped_at;
END;
$$;

CREATE OR REPLACE PROCEDURE raw.ingest_tabelog_review(
    p_restaurant_url TEXT,
    p_review_id TEXT,
    p_reviewer_name TEXT,
    p_review_text TEXT,
    p_rating NUMERIC(2,1),
    p_review_date DATE
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
BEGIN
    INSERT INTO raw.tabelog_reviews (
        restaurant_url,
        review_id,
        reviewer_name,
        review_text,
        rating,
        review_date,
        scraped_at
    )
    VALUES (
        p_restaurant_url,
        p_review_id,
        p_reviewer_name,
        p_review_text,
        p_rating,
        p_review_date,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (restaurant_url, review_id) DO UPDATE
    SET reviewer_name = EXCLUDED.reviewer_name,
        review_text = EXCLUDED.review_text,
        rating = EXCLUDED.rating,
        review_date = EXCLUDED.review_date,
        scraped_at = EXCLUDED.scraped_at;
END;
$$;

CREATE OR REPLACE PROCEDURE raw.ingest_tabelog_review_page(
    p_url TEXT,
    p_raw_html TEXT,
    p_status VARCHAR(20),
    p_error_message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = raw, pg_temp
AS $$
BEGIN
    INSERT INTO raw.tabelog_review_pages (
        url,
        raw_html,
        status,
        error_message,
        scraped_at
    )
    VALUES (
        p_url,
        p_raw_html,
        COALESCE(p_status, 'SUCCESS'),
        p_error_message,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (url) DO UPDATE
    SET raw_html = EXCLUDED.raw_html,
        status = EXCLUDED.status,
        error_message = EXCLUDED.error_message,
        scraped_at = EXCLUDED.scraped_at;
END;
$$;

GRANT EXECUTE ON PROCEDURE raw.ingest_japan_guide_page(TEXT, VARCHAR(50), TEXT, TEXT, VARCHAR(20), TEXT) TO tripsage_app;
GRANT EXECUTE ON PROCEDURE raw.ingest_tabelog_restaurant(TEXT, TEXT, VARCHAR(20), TEXT) TO tripsage_app;
GRANT EXECUTE ON PROCEDURE raw.ingest_tabelog_review(TEXT, TEXT, TEXT, TEXT, NUMERIC, DATE) TO tripsage_app;
GRANT EXECUTE ON PROCEDURE raw.ingest_tabelog_review_page(TEXT, TEXT, VARCHAR(20), TEXT) TO tripsage_app;
