# Glossier Product Scraper

A Python web scraper that collects product information from Glossier's All Products collection.

## Features

The scraper collects:

- Product name
- Product/variant ID
- Product URL
- Product images
- Price
- Product description
- Scraped timestamp

It also supports product variants and both India and US storefronts.

## Technologies

- Python
- Requests
- BeautifulSoup4
- Shopify JSON endpoint
- CSV

## Project Structure

```text
glossier-scraper/
│
├── scraper.py
├── requirements.txt
├── README.md
├── notes.txt
├── .gitignore
│
└── output/
    ├── products_india.csv
    └── products_us.csv
```

## Installation

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Run the Scraper

Open `scraper.py` and set the country.

### India

```python
COUNTRY = "india"
```

Run:

```powershell
py scraper.py
```

Output:

```text
output/products_india.csv
```

### US

Change the value to:

```python
COUNTRY = "us"
```

Run:

```powershell
py scraper.py
```

Output:

```text
output/products_us.csv
```

## Data Fields

| Field | Description |
|---|---|
| `product_name` | Product or variant name |
| `product_id` | Unique product/variant ID |
| `image` | Product image URLs |
| `url` | Product page URL |
| `price` | Product/variant price |
| `description` | Product description |
| `scraped_at` | Scraping timestamp |

## Variants

Variants are treated as separate products.

The Shopify variant ID is used as the unique `product_id`.

## Validation

India:

- 321 records
- 321 unique IDs
- 0 duplicate IDs

US:

- 353 records
- 353 unique IDs
- 0 duplicate IDs

## Notes

More details about the scraping approach, validation and AI usage are available in `notes.txt`.