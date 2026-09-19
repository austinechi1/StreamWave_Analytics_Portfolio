# Data Dictionary

Each row represents viewing activity for one content title in one month, country, subscription tier, and primary device combination. The raw file intentionally contains a small number of quality issues for cleaning practice.

| Column | Type after cleaning | Description |
|---|---|---|
| `row_id` | BIGINT | Raw record identifier |
| `content_id` | TEXT | Stable synthetic title identifier |
| `title` | TEXT | Synthetic movie or series title |
| `content_type` | TEXT | Movie or Series |
| `genre` | TEXT | Primary content genre |
| `original_language` | TEXT | Original production language |
| `release_date` | DATE | Platform release date |
| `report_month` | DATE | First day of the reporting month |
| `country` | TEXT | Viewer market |
| `region` | TEXT | Geographic region |
| `available_globally` | BOOLEAN | Whether the title received a global release |
| `subscription_tier` | TEXT | Ad-Supported, Standard, or Premium |
| `primary_device` | TEXT | Device associated with viewing activity |
| `runtime_minutes` | SMALLINT | Movie runtime or typical episode runtime |
| `season_count` | SMALLINT | Number of seasons; zero for movies |
| `episode_count` | SMALLINT | Episodes represented; one for movies |
| `views` | BIGINT | Estimated completed-view equivalents |
| `hours_viewed` | BIGINT | Total hours consumed |
| `completion_rate` | NUMERIC | Share of available runtime completed, from 0 to 1 |
| `user_rating` | NUMERIC | Average rating on a 10-point scale |
| `estimated_revenue_usd` | NUMERIC | Modeled revenue attributed to the activity |

## Derived fields

| Column | Description |
|---|---|
| `monthly_view_share` | Record's views divided by all platform views in the same month |
| `title_age_months` | Months between release date and reporting month |

## Embedded patterns

- Viewing rises during June–July and November–December.
- New titles receive a launch boost that decays with age.
- Drama and romance perform more strongly in selected Asian markets.
- Drama and comedy receive a moderate lift in Nigeria and South Africa.
- Mobile viewing has slightly lower completion than other devices.
- Ad-supported viewing earns more revenue per view than Standard in this fictional model.

## Intentional raw-data issues

- 35 duplicate business-key records
- Missing user ratings and completion rates
- Inconsistent capitalization and extra spaces in genre and country values
- Records where the report month predates the release date

