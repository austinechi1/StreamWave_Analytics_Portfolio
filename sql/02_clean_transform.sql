DROP TABLE IF EXISTS streamwave.viewing_clean;

CREATE TABLE streamwave.viewing_clean AS
WITH standardized AS (
    SELECT
        row_id::BIGINT AS source_row_id,
        UPPER(TRIM(content_id)) AS content_id,
        INITCAP(TRIM(title)) AS title,
        INITCAP(TRIM(content_type)) AS content_type,
        INITCAP(TRIM(genre)) AS genre,
        INITCAP(TRIM(original_language)) AS original_language,
        release_date::DATE AS release_date,
        report_month::DATE AS report_month,
        INITCAP(TRIM(country)) AS country,
        INITCAP(TRIM(region)) AS region,
        CASE WHEN LOWER(TRIM(available_globally)) IN ('yes','y','true','1') THEN TRUE ELSE FALSE END AS available_globally,
        INITCAP(TRIM(subscription_tier)) AS subscription_tier,
        INITCAP(TRIM(primary_device)) AS primary_device,
        NULLIF(runtime_minutes, '')::SMALLINT AS runtime_minutes,
        NULLIF(season_count, '')::SMALLINT AS season_count,
        NULLIF(episode_count, '')::SMALLINT AS episode_count,
        NULLIF(views, '')::BIGINT AS views,
        NULLIF(hours_viewed, '')::BIGINT AS hours_viewed,
        NULLIF(completion_rate, '')::NUMERIC(5,3) AS completion_rate,
        NULLIF(user_rating, '')::NUMERIC(3,1) AS user_rating,
        NULLIF(estimated_revenue_usd, '')::NUMERIC(14,2) AS estimated_revenue_usd,
        ROW_NUMBER() OVER (
            PARTITION BY UPPER(TRIM(content_id)), report_month, INITCAP(TRIM(country)),
                         INITCAP(TRIM(subscription_tier)), INITCAP(TRIM(primary_device))
            ORDER BY row_id::BIGINT
        ) AS duplicate_rank
    FROM streamwave.viewing_raw
), valid AS (
    SELECT * FROM standardized
    WHERE duplicate_rank = 1
      AND content_type IN ('Movie', 'Series')
      AND views >= 0 AND hours_viewed >= 0
      AND runtime_minutes BETWEEN 1 AND 500
      AND report_month >= release_date
)
SELECT
    source_row_id, content_id, title, content_type, genre, original_language,
    release_date, report_month, country, region, available_globally,
    subscription_tier, primary_device, runtime_minutes, season_count,
    episode_count, views, hours_viewed,
    COALESCE(completion_rate, AVG(completion_rate) OVER (PARTITION BY content_type, genre))::NUMERIC(5,3) AS completion_rate,
    COALESCE(user_rating, AVG(user_rating) OVER (PARTITION BY content_type, genre))::NUMERIC(3,1) AS user_rating,
    estimated_revenue_usd,
    (views / NULLIF(SUM(views) OVER (PARTITION BY report_month), 0)::NUMERIC)::NUMERIC(10,8) AS monthly_view_share,
    EXTRACT(YEAR FROM AGE(report_month, release_date))::INT * 12
      + EXTRACT(MONTH FROM AGE(report_month, release_date))::INT AS title_age_months
FROM valid;

ALTER TABLE streamwave.viewing_clean ADD PRIMARY KEY (source_row_id);
CREATE INDEX idx_viewing_month ON streamwave.viewing_clean(report_month);
CREATE INDEX idx_viewing_content ON streamwave.viewing_clean(content_id);
CREATE INDEX idx_viewing_country ON streamwave.viewing_clean(country);
CREATE INDEX idx_viewing_genre ON streamwave.viewing_clean(genre);

-- Quality checks
SELECT
    (SELECT COUNT(*) FROM streamwave.viewing_raw) AS raw_rows,
    COUNT(*) AS clean_rows,
    COUNT(*) FILTER (WHERE completion_rate IS NULL) AS null_completion_rates,
    COUNT(*) FILTER (WHERE user_rating IS NULL) AS null_ratings,
    COUNT(*) - COUNT(DISTINCT (content_id, report_month, country, subscription_tier, primary_device)) AS remaining_duplicates
FROM streamwave.viewing_clean;

