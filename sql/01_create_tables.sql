-- PostgreSQL 14+
CREATE SCHEMA IF NOT EXISTS streamwave;

DROP TABLE IF EXISTS streamwave.viewing_raw;
CREATE TABLE streamwave.viewing_raw (
    row_id TEXT, content_id TEXT, title TEXT, content_type TEXT, genre TEXT,
    original_language TEXT, release_date TEXT, report_month TEXT, country TEXT,
    region TEXT, available_globally TEXT, subscription_tier TEXT,
    primary_device TEXT, runtime_minutes TEXT, season_count TEXT,
    episode_count TEXT, views TEXT, hours_viewed TEXT, completion_rate TEXT,
    user_rating TEXT, estimated_revenue_usd TEXT
);

-- Run from psql while positioned at the repository root.
\copy streamwave.viewing_raw FROM 'data/raw/streamwave_viewing_raw.csv' WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');

SELECT COUNT(*) AS imported_rows FROM streamwave.viewing_raw;

