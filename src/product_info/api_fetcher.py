import requests

def get_product_info(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 1:
            return data["product"]
        else:
            return f"Product not found"
    else:
        return f"Error connection with the API: {response.status_code}"
