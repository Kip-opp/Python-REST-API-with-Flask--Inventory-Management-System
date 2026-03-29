import unittest
from unittest.mock import patch, MagicMock


class TestCLI(unittest.TestCase):

    @patch("cli_tool.requests.get")
    def test_list_items(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: [
            {"id": 1, "name": "Milk", "brand": "Silk", "price": 350, "stock": 10, "barcode": "123"}
        ])
        import cli_tool
        cli_tool.list_items()

    @patch("cli_tool.requests.get")
    def test_show_item_found(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"id": 1, "name": "Milk"})
        import cli_tool
        cli_tool.show_item(1)

    @patch("cli_tool.requests.get")
    def test_show_item_not_found(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404, json=lambda: {"error": "Not found"})
        import cli_tool
        cli_tool.show_item(9999)

    @patch("cli_tool.requests.delete")
    def test_delete_item(self, mock_del):
        mock_del.return_value = MagicMock(status_code=204)
        import cli_tool
        cli_tool.delete_item(1)


if __name__ == "__main__":
    unittest.main()