import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from app.routes import inventory
from external.openfoodfacts import fetch_by_barcode, fetch_by_name


class TestExternalAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.snapshot = [item.copy() for item in inventory]

    def tearDown(self):
        inventory[:] = self.snapshot

    @patch("external.openfoodfacts.requests.get")
    def test_fetch_by_barcode(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "status": 1,
            "product": {"product_name": "Almond Milk", "brands": "Silk", "ingredients_text": "Water, almonds", "nutriscore_grade": "a"}
        }
        mock_get.return_value = mock_resp
        data = fetch_by_barcode("3017624010701")
        self.assertEqual(data["status"], 1)

    @patch("external.openfoodfacts.requests.get")
    def test_fetch_by_name(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"products": [{"product_name": "Oat Milk", "brands": "Oatly"}]}
        mock_get.return_value = mock_resp
        data = fetch_by_name("oat milk")
        self.assertIn("products", data)

    def test_external_route_no_params_returns_400(self):
        res = self.client.get("/external/product")
        self.assertEqual(res.status_code, 400)

    @patch("external.openfoodfacts.requests.get")
    def test_external_route_barcode_returns_200(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"status": 1, "product": {"product_name": "Milk", "brands": "Arla"}}
        mock_get.return_value = mock_resp
        res = self.client.get("/external/product?barcode=3017624010701")
        self.assertEqual(res.status_code, 200)

    @patch("external.openfoodfacts.requests.get")
    def test_external_route_not_found_returns_404(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"status": 0}
        mock_get.return_value = mock_resp
        res = self.client.get("/external/product?barcode=0000000")
        self.assertEqual(res.status_code, 404)

    @patch("external.openfoodfacts.requests.get")
    def test_import_route_adds_to_inventory(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "status": 1,
            "product": {"product_name": "Test Milk", "brands": "Test", "ingredients_text": "Water", "nutriscore_grade": "b"}
        }
        mock_get.return_value = mock_resp
        before = len(inventory)
        res = self.client.post("/external/product/import", json={"barcode": "111222333", "price": 200, "stock": 5})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(inventory), before + 1)


if __name__ == "__main__":
    unittest.main()