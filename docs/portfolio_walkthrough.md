# Portfolio Walkthrough and Screenshot Plan

Use this sequence when presenting the project on GitHub, LinkedIn, or in an interview.

## 1. Introduce the business problem

Explain that StreamWave is a fictional global streaming platform that wants to understand content performance, engagement, regional preferences, device behavior, and subscription-tier economics.

**Screenshot 1:** The first 10–15 rows of `streamwave_viewing_raw.csv` in a spreadsheet or database grid. Crop the image so the headers remain readable.

## 2. Show the database setup

Run `01_create_tables.sql`, then show the imported row count.

**Screenshot 2:** PostgreSQL/pgAdmin showing `15,035` imported raw rows and the table name in the object browser.

## 3. Demonstrate cleaning skill

Run `02_clean_transform.sql`. Explain standardization, type conversion, duplicate removal, validation, null imputation, indexes, and derived metrics.

**Screenshot 3:** Place the CTE and `ROW_NUMBER()` duplicate logic on screen.

**Screenshot 4:** Show the final quality-check result. The most important fields are raw rows, clean rows, remaining duplicates, and remaining nulls.

## 4. Answer business questions

Run selected queries from `03_analysis_queries.sql`.

**Screenshot 5:** Top 10 titles query and results.

**Screenshot 6:** Month-over-month trend query and results. Keep the `LAG()` window function visible.

**Screenshot 7:** Regional genre ranking query. Keep `DENSE_RANK()` visible.

**Screenshot 8:** High-potential titles query and results. This is a strong closing SQL screenshot because it combines benchmarks, aggregation, and business logic.

## 5. Present the Python EDA

Run `python python/eda_analysis.py`.

**Screenshot 9:** A code section from `clean_data()` beside the console summary.

Use the six PNG files in `/images` directly in the README. The most important hero visual is `03_genre_reach_completion.png` because it compares reach, engagement, and rating in one chart.

## 6. Close with recommendations

Speak in business terms:

1. Protect the year-end content calendar because December is the peak viewing month.
2. Use drama as a reach anchor, while testing animation and web-device experiences for completion.
3. Improve mobile discovery and playback because mobile has the lowest completion rate.
4. Treat ad-supported users as a major monetization segment.
5. Promote locally resonant genres by region instead of using one global homepage strategy.

## Visual style

- Use a charcoal background, white text, and red accents.
- Keep screenshots at the same width.
- Add short captions that state the skill demonstrated, such as “Removing duplicates with a PostgreSQL window function.”
- Never show every query. Select the queries that demonstrate different skills.
- Avoid screenshots with unreadable full-screen code. Crop around the relevant logic and result.

