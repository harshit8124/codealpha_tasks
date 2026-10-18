"""
CodeAlpha Task 1: Web Scraping
Scrapes the Books to Scrape demo catalog and saves data/books.csv.
Run: python scrape_books.py
"""
import time
import re
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "books.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CodeAlphaLearningProject/1.0; educational use)"
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def get_soup(url):
    response = SESSION.get(url, timeout=25)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_rating(card):
    star = card.select_one("p.star-rating")
    if not star:
        return None
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for class_name in star.get("class", []):
        if class_name in rating_map:
            return rating_map[class_name]
    return None


def scrape_category(category_name, category_url):
    rows = []
    page_url = category_url
    while page_url:
        soup = get_soup(page_url)
        for card in soup.select("article.product_pod"):
            title = card.select_one("h3 a")
            price = card.select_one(".price_color")
            stock = card.select_one(".availability")
            link = title.get("href", "") if title else ""
            rows.append({
                "title": title.get("title", title.get_text(strip=True)) if title else None,
                "price_gbp": float(re.sub(r"[^0-9.]", "", price.get_text(strip=True))) if price else None,
                "rating": parse_rating(card),
                "availability": " ".join(stock.get_text(" ", strip=True).split()) if stock else None,
                "category": category_name,
                "product_url": urljoin(page_url, link),
            })
        next_link = soup.select_one("li.next a")
        page_url = urljoin(page_url, next_link.get("href")) if next_link else None
        time.sleep(0.15)
    return rows


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    soup = get_soup(BASE_URL)
    categories = []
    for link in soup.select("div.side_categories ul li ul li a"):
        href = link.get("href")
        name = link.get_text(strip=True)
        if href:
            categories.append((name, urljoin(BASE_URL, href)))

    all_rows = []
    for i, (name, url) in enumerate(categories, start=1):
        print(f"[{i}/{len(categories)}] Scraping category: {name}")
        try:
            all_rows.extend(scrape_category(name, url))
        except requests.RequestException as exc:
            print(f"  WARNING: skipped category {name!r}: {exc}")

    df = pd.DataFrame(all_rows)
    if df.empty:
        raise RuntimeError(
            "No books were scraped. Check your internet connection and try again."
        )
    df = df.drop_duplicates(subset=["product_url"]).reset_index(drop=True)
    df["availability"] = df["availability"].str.replace(r"\s+", " ", regex=True).str.strip()
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\nSaved {len(df):,} unique books to {OUTPUT_FILE}")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
