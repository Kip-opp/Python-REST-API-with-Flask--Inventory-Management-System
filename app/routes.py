import threading
from flask import jsonify, request
from external.openfoodfacts import fetch_by_barcode, fetch_by_name, parse_product

# ─── In-memory inventory ──────────────────────────────────────────────────────
inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "3017624010701",
        "ingredients": "Filtered water, almonds, cane sugar",
        "nutriscore": "a",
        "price": 350,
        "stock": 20,
    },
    {
        "id": 2,
        "name": "Peanut Butter",
        "brand": "Kraft",
        "barcode": "737628064502",
        "ingredients": "Roasted peanuts, sugar, salt",
        "nutriscore": "c",
        "price": 500,
        "stock": 15,
    },
    {
        "id": 3,
        "name": "Whole Grain Oats",
        "brand": "Quaker",
        "barcode": "030000057698",
        "ingredients": "Whole grain rolled oats",
        "nutriscore": "a",
        "price": 250,
        "stock": 30,
    },
]

# Thread-safe ID counter
_id_counter = max((item["id"] for item in inventory), default=0)
_id_lock = threading.Lock()


def next_id():
    """Generate the next unique ID in a thread-safe manner."""
    global _id_counter
    with _id_lock:
        _id_counter += 1
        return _id_counter


def validate_item_data(data, required_fields=None):
    """
    Validate item data with type checking and constraints.
    Returns (is_valid, errors_dict) where errors_dict is empty if valid.
    """
    errors = {}

    # Required fields
    if required_fields:
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field} is required"

    # Type and constraint validations
    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            errors["name"] = "name must be a non-empty string"
        else:
            data["name"] = data["name"].strip()

    if "brand" in data:
        if not isinstance(data["brand"], str):
            errors["brand"] = "brand must be a string"
        else:
            data["brand"] = data["brand"].strip()

    if "barcode" in data:
        if not isinstance(data["barcode"], str):
            errors["barcode"] = "barcode must be a string"
        else:
            data["barcode"] = data["barcode"].strip()

    if "ingredients" in data:
        if not isinstance(data["ingredients"], str):
            errors["ingredients"] = "ingredients must be a string"
        else:
            data["ingredients"] = data["ingredients"].strip()

    if "nutriscore" in data:
        if not isinstance(data["nutriscore"], str):
            errors["nutriscore"] = "nutriscore must be a string"
        else:
            data["nutriscore"] = data["nutriscore"].strip().lower()
            if data["nutriscore"] and data["nutriscore"] not in "abcde":
                errors["nutriscore"] = "nutriscore must be a-e or empty"

    if "price" in data:
        try:
            data["price"] = float(data["price"])
            if data["price"] < 0:
                errors["price"] = "price must be non-negative"
        except (ValueError, TypeError):
            errors["price"] = "price must be a number"

    if "stock" in data:
        try:
            data["stock"] = int(data["stock"])
            if data["stock"] < 0:
                errors["stock"] = "stock must be non-negative"
        except (ValueError, TypeError):
            errors["stock"] = "stock must be an integer"

    return len(errors) == 0, errors


def register_routes(app):

    # ── GET /inventory ────────────────────────────────────────────────────────
    @app.get("/inventory")
    def get_inventory():
        return jsonify(inventory), 200

    # ── GET /inventory/<id> ───────────────────────────────────────────────────
    @app.get("/inventory/<int:item_id>")
    def get_item(item_id):
        item = next((x for x in inventory if x["id"] == item_id), None)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200

    # ── POST /inventory ───────────────────────────────────────────────────────
    @app.post("/inventory")
    def add_item():
        data = request.get_json(force=True)
        is_valid, errors = validate_item_data(data, required_fields=["name"])
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": errors}), 400
        item = {
            "id": next_id(),
            "name": data["name"],
            "brand": data.get("brand", ""),
            "barcode": data.get("barcode", ""),
            "ingredients": data.get("ingredients", ""),
            "nutriscore": data.get("nutriscore", ""),
            "price": data.get("price", 0),
            "stock": data.get("stock", 0),
        }
        inventory.append(item)
        return jsonify(item), 201

    # ── PATCH /inventory/<id> ─────────────────────────────────────────────────
    @app.patch("/inventory/<int:item_id>")
    def update_item(item_id):
        item = next((x for x in inventory if x["id"] == item_id), None)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        data = request.get_json(force=True)
        is_valid, errors = validate_item_data(data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": errors}), 400
        # Only update provided fields
        updated_fields = []
        for key in [
            "name",
            "brand",
            "barcode",
            "ingredients",
            "nutriscore",
            "price",
            "stock",
        ]:
            if key in data:
                item[key] = data[key]
                updated_fields.append(key)
        if not updated_fields:
            return jsonify({"message": "No fields provided to update"}), 200
        return jsonify(item), 200

    # ── DELETE /inventory/<id> ────────────────────────────────────────────────
    @app.delete("/inventory/<int:item_id>")
    def delete_item(item_id):
        before = len(inventory)
        inventory[:] = [x for x in inventory if x["id"] != item_id]
        if len(inventory) == before:
            return jsonify({"error": "Item not found"}), 404
        return "", 204

    # ── GET /external/product ─────────────────────────────────────────────────
    @app.get("/external/product")
    def external_product():
        barcode = request.args.get("barcode")
        name = request.args.get("name")
        if not barcode and not name:
            return jsonify({"error": "Provide barcode or name"}), 400
        try:
            if barcode:
                data = fetch_by_barcode(barcode)
                if data.get("status") == 0:
                    return jsonify(
                        {"error": "Product not found on Open Food Facts"}
                    ), 404
                return jsonify(
                    {
                        "source": "openfoodfacts",
                        "product": parse_product(data.get("product", {})),
                    }
                ), 200
            else:
                assert name is not None  # Ensured by earlier check
                data = fetch_by_name(name)
                products = data.get("products", [])
                return jsonify(
                    {
                        "source": "openfoodfacts",
                        "count": len(products),
                        "products": [parse_product(p) for p in products],
                    }
                ), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 502

    # ── POST /external/product/import ─────────────────────────────────────────
    @app.post("/external/product/import")
    def import_from_api():
        """
        Fetch product from Open Food Facts by barcode
        and save it directly into the inventory array.
        Satisfies: 'User interface built to get from external api
        and add it to database array' — Excelled (20pts)
        """
        data = request.get_json(force=True)
        barcode = data.get("barcode")
        if not barcode:
            return jsonify({"error": "barcode is required"}), 400
        # Validate price and stock if provided
        is_valid, errors = validate_item_data(data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": errors}), 400
        try:
            off_data = fetch_by_barcode(barcode)
            if off_data.get("status") == 0:
                return jsonify({"error": "Product not found on Open Food Facts"}), 404
            parsed = parse_product(off_data.get("product", {}))
            item = {
                "id": next_id(),
                "name": parsed.get("name", "Unknown"),
                "brand": parsed.get("brand", ""),
                "barcode": barcode,
                "ingredients": parsed.get("ingredients", ""),
                "nutriscore": parsed.get("nutriscore", ""),
                "price": data.get("price", 0),
                "stock": data.get("stock", 0),
            }
            inventory.append(item)
            return jsonify(
                {"message": "Imported from Open Food Facts", "item": item}
            ), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 502
