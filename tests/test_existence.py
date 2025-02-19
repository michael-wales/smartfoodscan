def test_reality_is_real():
    assert True

# some example tests
import requests
from src.api_fetcher import get_product_info

def test_get_product_info_success():
    """Test a valid API call returns expected keys."""
    barcode = "3017620422003"  # Nutella barcode
    product = get_product_info(barcode)
    assert product is not None
    assert "product_name" in product
    assert "code" in product

def test_get_product_info_invalid():
    """Test an invalid barcode returns None."""
    barcode = "0000000000000"  # Non-existent barcode
    product = get_product_info(barcode)
    assert product is None
    # This should fail because the code currently does not return None (however the app requires a null return)

def test_api_response_status():
    """Test API returns a 200 status code."""
    barcode = "3017620422003"
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    assert response.status_code == 200
