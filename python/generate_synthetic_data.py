"""Generate a reproducible, intentionally imperfect streaming-viewership dataset."""

from __future__ import annotations

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260918
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "streamwave_viewing_raw.csv"

COUNTRIES = {
    "United States": ("North America", 1.00), "Canada": ("North America", .46),
    "Brazil": ("Latin America", .65), "Mexico": ("Latin America", .58),
    "United Kingdom": ("Europe", .62), "Germany": ("Europe", .56),
    "France": ("Europe", .51), "Spain": ("Europe", .43),
    "Nigeria": ("Africa", .35), "South Africa": ("Africa", .34),
    "India": ("Asia", .82), "Japan": ("Asia", .47), "South Korea": ("Asia", .55),
    "Australia": ("Oceania", .39),
}
GENRES = ["Drama", "Comedy", "Thriller", "Documentary", "Action", "Romance", "Sci-Fi", "Crime", "Animation"]
LANGUAGES = ["English", "Spanish", "Korean", "Hindi", "French", "German", "Portuguese", "Japanese", "Yoruba"]
DEVICES = {"Smart TV": .38, "Mobile": .29, "Web": .14, "Tablet": .09, "Game Console": .10}
TIERS = {"Ad-Supported": .36, "Standard": .43, "Premium": .21}
TITLE_WORDS_A = ["Silent", "Golden", "Last", "Hidden", "Midnight", "Northern", "Broken", "Electric", "Wild", "Second", "Crimson", "Infinite"]
TITLE_WORDS_B = ["Signal", "Kingdom", "Promise", "Harbor", "Code", "Road", "Summer", "Witness", "Pulse", "Crown", "Echo", "Fire"]


def weighted_choice(options: dict[str, float]) -> str:
    return random.choices(list(options), weights=list(options.values()), k=1)[0]


def month_starts(start: date, count: int):
    year, month = start.year, start.month
    for _ in range(count):
        yield date(year, month, 1)
        month += 1
        if month == 13:
            year, month = year + 1, 1


def build_catalog(n: int = 180) -> list[dict]:
    catalog = []
    used = set()
    for i in range(1, n + 1):
        while True:
            title = f"{random.choice(TITLE_WORDS_A)} {random.choice(TITLE_WORDS_B)}"
            if title not in used:
                used.add(title)
                break
            title += f" {i}"
            if title not in used:
                used.add(title)
                break
        content_type = random.choices(["Movie", "Series"], [.57, .43])[0]
        genre = random.choices(GENRES, [18, 15, 13, 8, 12, 11, 7, 9, 7], k=1)[0]
        language = random.choices(LANGUAGES, [50, 12, 8, 8, 6, 4, 6, 4, 2], k=1)[0]
        runtime = random.randint(78, 148) if content_type == "Movie" else random.randint(22, 62)
        episodes = 1 if content_type == "Movie" else random.randint(6, 12)
        release = date(2022, 1, 1) + timedelta(days=random.randint(0, 1460))
        catalog.append({
            "content_id": f"SW{i:04d}", "title": title, "content_type": content_type,
            "genre": genre, "original_language": language, "release_date": release,
            "runtime_minutes": runtime, "season_count": 0 if content_type == "Movie" else random.randint(1, 4),
            "episode_count": episodes, "quality": random.lognormvariate(0, .65),
            "global_release": random.random() < .68,
        })
    return catalog


def generate(rows_target: int = 15000) -> list[dict]:
    random.seed(SEED)
    catalog = build_catalog()
    months = list(month_starts(date(2025, 1, 1), 18))
    rows = []
    for row_id in range(1, rows_target + 1):
        item = random.choices(catalog, weights=[x["quality"] for x in catalog], k=1)[0]
        country = random.choices(list(COUNTRIES), weights=[COUNTRIES[c][1] for c in COUNTRIES], k=1)[0]
        region, market = COUNTRIES[country]
        report_month = random.choice(months)
        age_months = max(0, (report_month.year - item["release_date"].year) * 12 + report_month.month - item["release_date"].month)
        release_decay = .42 + 1.6 * math.exp(-age_months / 5)
        seasonality = 1.18 if report_month.month in (11, 12) else (1.10 if report_month.month in (6, 7) else 1.0)
        genre_lift = 1.25 if (country in ("South Korea", "Japan") and item["genre"] in ("Drama", "Romance")) else 1.0
        if country in ("Nigeria", "South Africa") and item["genre"] in ("Drama", "Comedy"):
            genre_lift *= 1.18
        device = weighted_choice(DEVICES)
        tier = weighted_choice(TIERS)
        base = 72000 * market * item["quality"] * release_decay * seasonality * genre_lift
        views = max(120, int(random.lognormvariate(math.log(max(base, 150)), .55)))
        completion = min(.96, max(.18, random.gauss(.72, .11) + (.05 if item["content_type"] == "Series" else 0) - (.04 if device == "Mobile" else 0)))
        hours = int(views * item["runtime_minutes"] * (item["episode_count"] if item["content_type"] == "Series" else 1) * completion / 60)
        rating = min(9.8, max(3.5, random.gauss(6.3 + math.log1p(item["quality"]) * .9, .65)))
        revenue = views * {"Ad-Supported": .018, "Standard": .012, "Premium": .016}[tier] * random.uniform(.90, 1.10)
        rows.append({
            "row_id": row_id, "content_id": item["content_id"], "title": item["title"],
            "content_type": item["content_type"], "genre": item["genre"], "original_language": item["original_language"],
            "release_date": item["release_date"].isoformat(), "report_month": report_month.isoformat(),
            "country": country, "region": region, "available_globally": "Yes" if item["global_release"] else "No",
            "subscription_tier": tier, "primary_device": device, "runtime_minutes": item["runtime_minutes"],
            "season_count": item["season_count"], "episode_count": item["episode_count"], "views": views,
            "hours_viewed": hours, "completion_rate": round(completion, 3), "user_rating": round(rating, 1),
            "estimated_revenue_usd": round(revenue, 2),
        })

    # Inject realistic data-quality problems for the SQL cleaning stage.
    for idx in random.sample(range(len(rows)), 105):
        rows[idx]["genre"] = rows[idx]["genre"].lower() if idx % 2 else f" {rows[idx]['genre']} "
    for idx in random.sample(range(len(rows)), 70):
        rows[idx]["user_rating"] = ""
    for idx in random.sample(range(len(rows)), 45):
        rows[idx]["completion_rate"] = ""
    for idx in random.sample(range(len(rows)), 30):
        rows[idx]["country"] = rows[idx]["country"].upper()
    for original in random.sample(rows, 35):
        duplicate = dict(original)
        duplicate["row_id"] = len(rows) + 1
        rows.append(duplicate)
    return rows


def main():
    rows = generate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {len(rows):,} rows at {OUTPUT}")


if __name__ == "__main__":
    main()
