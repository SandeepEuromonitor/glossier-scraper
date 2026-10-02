import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import csv
import json
import os
import re

BASE_URL = "https://www.glossier.com"

COUNTRY = "us"

if COUNTRY == "india":
    COLLECTION_URL = f"{BASE_URL}/en-in/collections/all"
    OUTPUT_FILE = os.path.join(
        "output",
        "products_india.csv"
    )

elif COUNTRY == "us":
    COLLECTION_URL = f"{BASE_URL}/collections/all"
    OUTPUT_FILE = os.path.join(
        "output",
        "products_us.csv"
    )

else:
    raise ValueError("COUNTRY must be 'india' or 'us'")

OUTPUT_DIR = "output"

# Stretch Task 4
# False = normal products
# True  = each variant becomes a separate product
INCLUDE_VARIANTS = True

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
}


def get_products_from_collection():
    """
    Get all products from the Glossier collection.
    """

    products = []
    page = 1

    while True:

        url = (
            f"{COLLECTION_URL}/products.json"
            f"?limit=250&page={page}"
        )

        response = requests.get(url, headers=HEADERS, timeout=30)

        if response.status_code != 200:
            break

        try:
            data = response.json()
        except ValueError:
            break

        page_products = data.get("products", [])

        if not page_products:
            break

        products.extend(page_products)

        print(
            f"Collection page {page}: "
            f"{len(page_products)} products"
        )

        if len(page_products) < 250:
            break

        page += 1

    return products


def get_product_description(product_url):
    """
    Visit the individual product page and extract its description.
    """

    response = requests.get(
        product_url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # First preference: meta description
    description_tag = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if description_tag:
        description = description_tag.get("content", "").strip()

        if description and description.upper() != "US":
            return description

    # Second preference: Shopify JSON product description
    match = re.search(
        r'"description":"(.*?)"',
        response.text,
        re.DOTALL
    )

    if match:
        description = match.group(1)

        description = (
            description
            .replace("\\/", "/")
            .replace('\\"', '"')
        )

        description = BeautifulSoup(
            description,
            "html.parser"
        ).get_text(" ", strip=True)

        if description.upper() != "US":
            return description

    return ""


def get_images(product):
    """
    Extract all product image URLs.
    """

    images = []

    for image in product.get("images", []):

        src = image.get("src")

        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src

        images.append(src)

    return images


def get_product_price(product):
    """
    Get the product price from its variants.
    """

    variants = product.get("variants", [])

    if not variants:
        return ""

    prices = []

    for variant in variants:

        price = variant.get("price")

        if price is not None:
            prices.append(str(price))

    if not prices:
        return ""

    return min(prices, key=lambda x: float(x))


def build_normal_product(product):
    """
    Create one CSV record for one product.
    """

    product_id = str(product.get("id", ""))

    handle = product.get("handle", "")

    product_url = f"{BASE_URL}/products/{handle}"

    product_name = product.get("title", "")

    images = get_images(product)

    price = get_product_price(product)

    print(f"Scraping: {product_name}")

    description = get_product_description(product_url)

    scraped_at = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "product_name": product_name,
        "product_id": product_id,
        "image": json.dumps(images),
        "url": product_url,
        "price": price,
        "description": description,
        "scraped_at": scraped_at
    }


def build_variant_products(product):
    """
    Stretch Task 4:
    Treat every variant as a unique product.
    """

    rows = []

    product_name = product.get("title", "")

    handle = product.get("handle", "")

    product_url = f"{BASE_URL}/products/{handle}"

    images = get_images(product)

    description = get_product_description(product_url)

    for variant in product.get("variants", []):

        variant_id = str(
            variant.get("id", "")
        )

        variant_title = variant.get(
            "title",
            ""
        )

        price = str(
            variant.get("price", "")
        )

        if variant_title == "Default Title":
            variant_name = product_name
        else:
            variant_name = (
                f"{product_name} - "
                f"{variant_title}"
            )

        scraped_at = datetime.now(
            timezone.utc
        ).isoformat()

        rows.append({
            "product_name": variant_name,
            "product_id": variant_id,
            "image": json.dumps(images),
            "url": product_url,
            "price": price,
            "description": description,
            "scraped_at": scraped_at
        })

    return rows


def main():

    print("=" * 60)
    print("Glossier Product Scraper")
    print("=" * 60)

    print("\nGetting products from collection...")

    products = get_products_from_collection()

    print(
        f"\nTotal products found: {len(products)}"
    )

    if not products:
        print(
            "No products found."
        )
        return

    rows = []

    for product in products:

        if INCLUDE_VARIANTS:
            variant_rows = build_variant_products(
                product
            )

            rows.extend(variant_rows)

        else:
            row = build_normal_product(
                product
            )

            rows.append(row)

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    fieldnames = [
        "product_name",
        "product_id",
        "image",
        "url",
        "price",
        "description",
        "scraped_at"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 60)
    print("Scraping completed!")
    print("Products written:", len(rows))
    print("CSV:", OUTPUT_FILE)
    print("=" * 60)


if __name__ == "__main__":
    main()