import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {
    "User-Agent": "InventoryManagementSystem/1.0 (moringa-student@email.com)"
}


def fetch_by_barcode(barcode: str) -> dict:
    """
    Fetch a product from Open Food Facts using barcode via API v2.
    Endpoint: GET /api/v2/product/{barcode}.json
    Docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
    """
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_by_name(name: str) -> dict:
    """
    Search products on Open Food Facts by name.
    Endpoint: GET /cgi/search.pl
    Docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
    """
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,
    }
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_product(product: dict) -> dict:
    """Extract clean, relevant fields from an Open Food Facts product object."""
    return {
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", ""),
        "barcode": product.get("code", product.get("_id", "")),
        "ingredients": product.get("ingredients_text", ""),
        "nutriscore": product.get("nutriscore_grade", ""),
    }