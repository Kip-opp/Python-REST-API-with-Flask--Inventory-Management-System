import unittest
from app import create_app
from app.routes import inventory


class TestInventoryRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.snapshot = [item.copy() for item in inventory]

    def tearDown(self):
        inventory[:] = self.snapshot

    def test_get_all_inventory_returns_200(self):
        res = self.client.get("/inventory")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_single_item_returns_200(self):
        res = self.client.get("/inventory/1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["id"], 1)

    def test_get_missing_item_returns_404(self):
        res = self.client.get("/inventory/9999")
        self.assertEqual(res.status_code, 404)

    def test_post_new_item_returns_201(self):
        payload = {"name": "Green Tea", "brand": "Tetley", "barcode": "9999", "price": 120, "stock": 8}
        res = self.client.post("/inventory", json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()["name"], "Green Tea")

    def test_post_missing_name_returns_400(self):
        res = self.client.post("/inventory", json={"brand": "Test"})
        self.assertEqual(res.status_code, 400)

    def test_patch_item_returns_200(self):
        res = self.client.patch("/inventory/1", json={"price": 999})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["price"], 999)

    def test_patch_missing_item_returns_404(self):
        res = self.client.patch("/inventory/9999", json={"price": 1})
        self.assertEqual(res.status_code, 404)

    def test_delete_item_returns_204(self):
        res = self.client.delete("/inventory/1")
        self.assertEqual(res.status_code, 204)

    def test_delete_missing_item_returns_404(self):
        res = self.client.delete("/inventory/9999")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()