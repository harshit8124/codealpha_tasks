"""
CodeAlpha Task 2: Exploratory Data Analysis (EDA)
Reads data/books.csv, cleans it, prints findings, and saves summary tables.
Run after scrape_books.py: python eda.py
"""
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

DATA_FILE = Path("data/books.csv")
OUT_DIR = Path("outputs")


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError("data/books.csv not found. Run `python scrape_books.py` first.")
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_FILE)
    print("\n=== 1. Dataset overview ===")
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    print("\nData types:\n", df.dtypes)
    print("\nMissing values:\n", df.isna().sum())
    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    df = df.drop_duplicates(subset=["product_url"]).copy()
    df["price_gbp"] = pd.to_numeric(df["price_gbp"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["category"] = df["category"].fillna("Unknown")
    df["availability"] = df["availability"].fillna("Unknown")

    print("\n=== 2. Numeric summary ===")
    print(df[["price_gbp", "rating"]].describe().round(2).to_string())

    category_summary = (
        df.groupby("category", dropna=False)
          .agg(book_count=("title", "count"),
               average_price_gbp=("price_gbp", "mean"),
               median_price_gbp=("price_gbp", "median"),
               average_rating=("rating", "mean"))
          .sort_values("book_count", ascending=False)
          .round(2)
    )
    category_summary.to_csv(OUT_DIR / "category_summary.csv")
    print("\n=== 3. Category summary (top 10 by book count) ===")
    print(category_summary.head(10).to_string())

    rating_summary = (
        df.groupby("rating", dropna=False)
          .agg(book_count=("title", "count"), average_price_gbp=("price_gbp", "mean"))
          .round(2)
    )
    rating_summary.to_csv(OUT_DIR / "rating_summary.csv")
    print("\n=== 4. Rating summary ===")
    print(rating_summary.to_string())

    print("\n=== 5. Questions investigated ===")
    print("Q1. Which categories contain the most books? See category_summary.csv.")
    print("Q2. How are prices distributed? See descriptive statistics and price histogram.")
    print("Q3. Do prices and star ratings move together? Spearman rank correlation below.")
    paired = df[["price_gbp", "rating"]].dropna()
    if len(paired) >= 3 and paired["price_gbp"].nunique() > 1 and paired["rating"].nunique() > 1:
        rho, p_value = spearmanr(paired["price_gbp"], paired["rating"])
        print(f"Spearman rho={rho:.3f}, p-value={p_value:.4g}, n={len(paired)}")
        print("Interpretation: correlation describes association, not causation.")
    else:
        print("Not enough varied, complete observations to calculate correlation.")

    print("\n=== 6. Potential data quality issues ===")
    print("- Ratings are ordinal values (1 to 5), not continuous measurements.")
    print("- Prices are listed in GBP on this demo website.")
    print("- The website warns that prices/ratings are randomly assigned and have no real-world meaning.")
    print("- Missing values and duplicates were checked; category and availability blanks are labeled Unknown.")
    print("\nEDA complete. Summary tables saved in outputs/.")


if __name__ == "__main__":
    main()
