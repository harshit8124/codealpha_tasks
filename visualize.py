"""
CodeAlpha Task 3: Data Visualization
Creates charts in outputs/ using data/books.csv.
Run after scrape_books.py: python visualize.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = Path("data/books.csv")
OUT_DIR = Path("outputs")


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError("data/books.csv not found. Run `python scrape_books.py` first.")
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_FILE)
    df["price_gbp"] = pd.to_numeric(df["price_gbp"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["category"] = df["category"].fillna("Unknown")
    df["availability"] = df["availability"].fillna("Unknown")

    # 1. Price distribution
    prices = df["price_gbp"].dropna()
    if not prices.empty:
        plt.figure(figsize=(9, 5))
        plt.hist(prices, bins=20, edgecolor="black")
        plt.title("Distribution of Book Prices")
        plt.xlabel("Price (£ GBP)")
        plt.ylabel("Number of books")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "price_distribution.png", dpi=160)
        plt.close()

    # 2. Average price by category (top 12 categories by count)
    category_order = df["category"].value_counts().head(12).index
    avg_price = (df[df["category"].isin(category_order)]
                 .groupby("category")["price_gbp"].mean().sort_values())
    if not avg_price.empty:
        plt.figure(figsize=(10, 7))
        avg_price.plot(kind="barh")
        plt.title("Average Book Price by Category (Top Categories by Catalog Size)")
        plt.xlabel("Average price (£ GBP)")
        plt.ylabel("Category")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "average_price_by_category.png", dpi=160)
        plt.close()

    # 3. Rating distribution
    ratings = df["rating"].dropna().astype(int).value_counts().sort_index()
    if not ratings.empty:
        plt.figure(figsize=(8, 5))
        ratings.plot(kind="bar")
        plt.title("Book Star Rating Distribution")
        plt.xlabel("Star rating")
        plt.ylabel("Number of books")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(OUT_DIR / "rating_distribution.png", dpi=160)
        plt.close()

    # 4. Price vs rating
    paired = df[["price_gbp", "rating"]].dropna()
    if not paired.empty:
        plt.figure(figsize=(8, 5))
        plt.scatter(paired["rating"], paired["price_gbp"], alpha=0.65)
        plt.title("Book Price vs Star Rating")
        plt.xlabel("Star rating")
        plt.ylabel("Price (£ GBP)")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "price_vs_rating.png", dpi=160)
        plt.close()

    # 5. Availability status
    availability = df["availability"].value_counts().head(10)
    if not availability.empty:
        plt.figure(figsize=(8, 5))
        availability.plot(kind="bar")
        plt.title("Book Availability Status")
        plt.xlabel("Availability")
        plt.ylabel("Number of books")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "availability_status.png", dpi=160)
        plt.close()

    print("Charts saved to outputs/:")
    for path in sorted(OUT_DIR.glob("*.png")):
        print(" -", path)


if __name__ == "__main__":
    main()
