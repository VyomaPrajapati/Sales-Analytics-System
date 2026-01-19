import requests

def fetch_all_products():
    """
    Fetches all products from DummyJSON API.
    """
    url = "https://dummyjson.com/products?limit=100"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # We return the list of products found in the 'products' key
            return data.get('products', [])
        else:
            print(f"API Error: Received status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []

def create_product_mapping(api_products):
    """
    Creates a dictionary mapping product IDs to info for fast lookup.
    Uses .get() to prevent crashes if fields are missing.
    """
    mapping = {}
    for item in api_products:
        # We use .get(key, default) to handle missing data
        mapping[item['id']] = {
            'title': item.get('title', 'Unknown Product'),
            'category': item.get('category', 'General'),
            'brand': item.get('brand', 'Generic'),
            'rating': item.get('rating', 0.0)
        }
    return mapping