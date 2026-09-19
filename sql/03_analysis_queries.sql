-- Q1. Which titles attracted the most views?
SELECT
    title,
    content_type,
    genre,
    SUM(views) AS total_views,
    SUM(hours_viewed) AS total_hours_viewed
FROM streamwave.viewing_clean
GROUP BY title, content_type, genre
ORDER BY total_views DESC
LIMIT 10;

-- Q2. Which genres combine scale with strong engagement?
SELECT
    genre,
    SUM(views) AS total_views,
    ROUND(AVG(completion_rate) * 100, 1) AS avg_completion_pct,
    ROUND(AVG(user_rating), 2) AS avg_rating
FROM streamwave.viewing_clean
GROUP BY genre
ORDER BY total_views DESC;

-- Q3. Month-over-month platform growth.
WITH
    monthly AS (
     SELECT
        report_month,
        SUM(views) AS views, SUM(hours_viewed) AS hours_viewed
    FROM streamwave.viewing_clean GROUP BY report_month
)
SELECT report_month, views, hours_viewed,
       ROUND(100.0 * (views - LAG(views) OVER (ORDER BY report_month))
             / NULLIF(LAG(views) OVER (ORDER BY report_month), 0), 2) AS views_mom_pct
FROM monthly ORDER BY report_month;

-- Q4. Regional taste: the leading genre in each region.
WITH ranked AS (
    SELECT region, genre, SUM(views) AS views,
           DENSE_RANK() OVER (PARTITION BY region ORDER BY SUM(views) DESC) AS genre_rank
    FROM streamwave.viewing_clean GROUP BY region, genre
)
SELECT region, genre, views FROM ranked WHERE genre_rank = 1 ORDER BY views DESC;

-- Q5. Which devices deliver the strongest completion?
SELECT primary_device, SUM(views) AS total_views,
       ROUND(AVG(completion_rate) * 100, 1) AS avg_completion_pct
FROM streamwave.viewing_clean
GROUP BY primary_device ORDER BY avg_completion_pct DESC;

-- Q6. Subscription-tier contribution.
SELECT subscription_tier, SUM(views) AS total_views,
       ROUND(SUM(estimated_revenue_usd), 2) AS estimated_revenue_usd,
       ROUND(SUM(estimated_revenue_usd) / NULLIF(SUM(views), 0), 4) AS revenue_per_view
FROM streamwave.viewing_clean GROUP BY subscription_tier
ORDER BY estimated_revenue_usd DESC;

-- Q7. Local-language opportunity by country.
SELECT country, original_language, SUM(views) AS views,
       ROUND(AVG(completion_rate) * 100, 1) AS avg_completion_pct
FROM streamwave.viewing_clean
WHERE original_language <> 'English'
GROUP BY country, original_language
HAVING SUM(views) >= 1000000
ORDER BY views DESC LIMIT 15;

-- Q8. Global releases versus limited releases.
SELECT available_globally, COUNT(DISTINCT content_id) AS titles,
       SUM(views) AS views, ROUND(AVG(user_rating), 2) AS avg_rating,
       ROUND(AVG(completion_rate) * 100, 1) AS avg_completion_pct
FROM streamwave.viewing_clean GROUP BY available_globally;

-- Q9. Content longevity by age bucket.
SELECT CASE WHEN title_age_months <= 3 THEN '0-3 months'
            WHEN title_age_months <= 12 THEN '4-12 months'
            WHEN title_age_months <= 24 THEN '13-24 months'
            ELSE '25+ months' END AS age_bucket,
       SUM(views) AS views, ROUND(AVG(completion_rate) * 100, 1) AS completion_pct
FROM streamwave.viewing_clean
GROUP BY 1 ORDER BY MIN(title_age_months);

-- Q10. High-potential titles: above-average completion and rating, meaningful reach.
WITH benchmarks AS (
    SELECT AVG(completion_rate) AS completion_benchmark,
           AVG(user_rating) AS rating_benchmark
    FROM streamwave.viewing_clean
)
SELECT title, genre, SUM(views) AS views,
       ROUND(AVG(completion_rate) * 100, 1) AS completion_pct,
       ROUND(AVG(user_rating), 2) AS rating
FROM streamwave.viewing_clean CROSS JOIN benchmarks
GROUP BY title, genre, completion_benchmark, rating_benchmark
HAVING AVG(completion_rate) > completion_benchmark
   AND AVG(user_rating) > rating_benchmark
   AND SUM(views) > 5000000
ORDER BY views DESC LIMIT 15;

