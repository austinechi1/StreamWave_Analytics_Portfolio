"""Create a cleaned CSV, summary tables, and portfolio-ready EDA charts."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "streamwave_viewing_raw.csv"
PROCESSED = ROOT / "data" / "processed" / "streamwave_viewing_clean.csv"
IMAGES = ROOT / "images"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = ["title", "content_type", "genre", "original_language", "country", "region", "subscription_tier", "primary_device"]
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip().str.title()
    df["content_id"] = df["content_id"].str.strip().str.upper()
    df["available_globally"] = df["available_globally"].str.strip().str.lower().eq("yes")
    for col in ["release_date", "report_month"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    numeric = ["runtime_minutes", "season_count", "episode_count", "views", "hours_viewed", "completion_rate", "user_rating", "estimated_revenue_usd"]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    key = ["content_id", "report_month", "country", "subscription_tier", "primary_device"]
    df = df.drop_duplicates(key, keep="first")
    df = df[df["report_month"].ge(df["release_date"]) & df["views"].ge(0) & df["runtime_minutes"].between(1, 500)].copy()
    df["completion_rate"] = df["completion_rate"].fillna(df.groupby(["content_type", "genre"])["completion_rate"].transform("mean"))
    df["user_rating"] = df["user_rating"].fillna(df.groupby(["content_type", "genre"])["user_rating"].transform("mean"))
    df["title_age_months"] = ((df["report_month"].dt.year - df["release_date"].dt.year) * 12 + df["report_month"].dt.month - df["release_date"].dt.month)
    return df


def save_chart(filename: str):
    plt.tight_layout()
    plt.savefig(IMAGES / filename, dpi=180, bbox_inches="tight")
    plt.close()


def main():
    sns.set_theme(style="whitegrid", palette="deep")
    IMAGES.mkdir(exist_ok=True)
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    df = clean_data(pd.read_csv(RAW))
    df.to_csv(PROCESSED, index=False)

    top = df.groupby("title", as_index=False)["views"].sum().nlargest(10, "views").sort_values("views")
    plt.figure(figsize=(10, 6)); sns.barplot(data=top, x="views", y="title", color="#E50914")
    plt.title("Top 10 Titles by Total Views"); plt.xlabel("Views"); plt.ylabel("")
    save_chart("01_top_titles.png")

    monthly = df.groupby("report_month", as_index=False).agg(views=("views", "sum"), hours_viewed=("hours_viewed", "sum"))
    plt.figure(figsize=(11, 5)); sns.lineplot(data=monthly, x="report_month", y="views", marker="o", color="#E50914")
    plt.title("Monthly Viewing Trend"); plt.xlabel(""); plt.ylabel("Views")
    save_chart("02_monthly_views.png")

    genre = df.groupby("genre", as_index=False).agg(views=("views", "sum"), completion_rate=("completion_rate", "mean"), user_rating=("user_rating", "mean"))
    plt.figure(figsize=(9, 6)); sns.scatterplot(data=genre, x="completion_rate", y="views", size="user_rating", hue="genre", sizes=(100, 450), legend="brief")
    plt.title("Genre Reach vs. Completion"); plt.xlabel("Average completion rate"); plt.ylabel("Views")
    save_chart("03_genre_reach_completion.png")

    device = df.groupby("primary_device", as_index=False)["completion_rate"].mean().sort_values("completion_rate", ascending=False)
    plt.figure(figsize=(8, 5)); sns.barplot(data=device, x="primary_device", y="completion_rate", color="#221F1F")
    plt.title("Completion Rate by Primary Device"); plt.xlabel(""); plt.ylabel("Average completion rate"); plt.ylim(0, 1)
    save_chart("04_device_completion.png")

    regional = df.pivot_table(index="region", columns="genre", values="views", aggfunc="sum", fill_value=0)
    regional = regional.div(regional.sum(axis=1), axis=0)
    plt.figure(figsize=(12, 6)); sns.heatmap(regional, cmap="Reds", annot=False)
    plt.title("Genre Share of Views by Region"); plt.xlabel(""); plt.ylabel("")
    save_chart("05_region_genre_heatmap.png")

    tier = df.groupby("subscription_tier", as_index=False)["estimated_revenue_usd"].sum().sort_values("estimated_revenue_usd", ascending=False)
    plt.figure(figsize=(7, 5)); sns.barplot(data=tier, x="subscription_tier", y="estimated_revenue_usd", color="#E50914")
    plt.title("Estimated Revenue by Subscription Tier"); plt.xlabel(""); plt.ylabel("Estimated revenue (USD)")
    save_chart("06_tier_revenue.png")

    summary = {
        "raw_rows": len(pd.read_csv(RAW)), "clean_rows": len(df), "titles": df["content_id"].nunique(),
        "countries": df["country"].nunique(), "months": df["report_month"].nunique(),
        "total_views": int(df["views"].sum()), "total_hours": int(df["hours_viewed"].sum()),
        "estimated_revenue": round(df["estimated_revenue_usd"].sum(), 2),
    }
    pd.Series(summary, name="value").to_csv(ROOT / "data" / "processed" / "project_summary.csv", header=True)
    print(pd.Series(summary).to_string())


if __name__ == "__main__":
    main()

