import argparse
import requests

BASE_URL = "http://127.0.0.1:5000"


def list_items():
    res = requests.get(f"{BASE_URL}/inventory")
    items = res.json()
    if not items:
        print("No items in inventory.")
        return
    print(f"\n{'ID':<5} {'Name':<28} {'Brand':<15} {'Price':<8} {'Stock':<8} Barcode")
    print("─" * 82)
    for item in items:
        print(
            f"{item['id']:<5} {item['name']:<28} {item.get('brand', ''):<15}"
            f" {item['price']:<8} {item['stock']:<8} {item.get('barcode', '')}"
        )
    print()


def show_item(item_id):
    res = requests.get(f"{BASE_URL}/inventory/{item_id}")
    if res.status_code == 404:
        print(f"Item {item_id} not found.")
        return
    print(f"\n--- Item #{item_id} ---")
    for k, v in res.json().items():
        print(f"  {k:<15}: {v}")
    print()


def add_item(args):
    payload = {
        "name": args.name,
        "brand": args.brand,
        "barcode": args.barcode,
        "price": args.price,
        "stock": args.stock,
    }
    res = requests.post(f"{BASE_URL}/inventory", json=payload)
    if res.status_code == 201:
        print(f"\n✓ Added: {res.json()}\n")
    else:
        print(f"✗ Error: {res.json()}")


def update_item(args):
    payload = {
        k: v for k, v in vars(args).items() if k not in {"cmd", "id"} and v is not None
    }
    if not payload:
        print("\n✗ No fields provided to update. Use --help for usage.\n")
        return
    res = requests.patch(f"{BASE_URL}/inventory/{args.id}", json=payload)
    if res.status_code == 200:
        response_data = res.json()
        if (
            "message" in response_data
            and "No fields provided" in response_data["message"]
        ):
            print(f"\n✓ No changes made: {response_data['message']}\n")
        else:
            print(f"\n✓ Updated: {response_data}\n")
    else:
        print(f"✗ Error: {res.json()}")


def delete_item(item_id):
    res = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    if res.status_code == 204:
        print(f"\n✓ Item {item_id} deleted.\n")
    else:
        print(f"✗ Error: {res.json()}")


def find_from_api(args):
    params = {}
    if args.barcode:
        params["barcode"] = args.barcode
    if args.name:
        params["name"] = args.name
    if not params:
        print("Provide --barcode or --name.")
        return
    res = requests.get(f"{BASE_URL}/external/product", params=params)
    if res.status_code != 200:
        print(f"✗ Error: {res.json().get('error')}")
        return
    data = res.json()
    if "product" in data:
        print(f"\n--- Found on Open Food Facts ---")
        for k, v in data["product"].items():
            print(f"  {k:<15}: {v}")
        print()
    elif "products" in data:
        print(f"\nFound {data['count']} result(s):\n")
        for p in data["products"]:
            print(f"  {p['name']} | {p['brand']} | barcode: {p['barcode']}")
        print()


def import_from_api(args):
    payload = {
        "barcode": args.barcode,
        "price": args.price,
        "stock": args.stock,
    }
    res = requests.post(f"{BASE_URL}/external/product/import", json=payload)
    if res.status_code == 201:
        print(f"\n✓ Imported into inventory:\n  {res.json()['item']}\n")
    else:
        print(f"✗ Error: {res.json().get('error')}")


def main():
    parser = argparse.ArgumentParser(
        prog="inventory-cli",
        description="Inventory Management CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inventory-cli list
  inventory-cli show 1
  inventory-cli add --name "Apple Juice" --price 150 --stock 20
  inventory-cli update 1 --price 200
  inventory-cli delete 1
  inventory-cli find-api --barcode 3017624010701
  inventory-cli import-api --barcode 3017624010701 --price 300

Commands:
  list                           List all inventory items
  show <id>                      Show one item by ID
  add --name --brand --barcode   Add item manually
  update <id> [fields...]        Update item fields
  delete <id>                    Delete an item
  find-api --barcode/--name      Search Open Food Facts
  import-api --barcode           Fetch from API and save to inventory
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="COMMAND")

    sub.add_parser("list", help="List all inventory items")

    show = sub.add_parser("show", help="Show details of a specific item")
    show.add_argument("id", type=int, help="Item ID to show")

    add = sub.add_parser("add", help="Add a new item to inventory")
    add.add_argument("--name", required=True, help="Item name")
    add.add_argument("--brand", default="", help="Item brand")
    add.add_argument("--barcode", default="", help="Item barcode")
    add.add_argument("--price", type=float, default=0, help="Item price")
    add.add_argument("--stock", type=int, default=0, help="Stock quantity")

    update = sub.add_parser("update", help="Update an existing item")
    update.add_argument("id", type=int, help="Item ID to update")
    update.add_argument("--name", help="Update item name")
    update.add_argument("--brand", help="Update item brand")
    update.add_argument("--barcode", help="Update item barcode")
    update.add_argument("--price", type=float, help="Update item price")
    update.add_argument("--stock", type=int, help="Update stock quantity")

    delete = sub.add_parser("delete", help="Delete an item from inventory")
    delete.add_argument("id", type=int, help="Item ID to delete")

    find_api = sub.add_parser("find-api", help="Search Open Food Facts API")
    find_api.add_argument("--barcode", help="Search by barcode")
    find_api.add_argument("--name", help="Search by product name")

    import_api = sub.add_parser(
        "import-api", help="Import product from Open Food Facts into inventory"
    )
    import_api.add_argument("--barcode", required=True, help="Barcode to import")
    import_api.add_argument(
        "--price", type=float, default=0, help="Set price for imported item"
    )
    import_api.add_argument(
        "--stock", type=int, default=0, help="Set stock for imported item"
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            print("\nError: Invalid command or arguments. Use --help for usage.\n")
            parser.print_usage()
        raise

    if args.cmd == "list":
        list_items()
    elif args.cmd == "show":
        show_item(args.id)
    elif args.cmd == "add":
        add_item(args)
    elif args.cmd == "update":
        update_item(args)
    elif args.cmd == "delete":
        delete_item(args.id)
    elif args.cmd == "find-api":
        find_from_api(args)
    elif args.cmd == "import-api":
        import_from_api(args)


if __name__ == "__main__":
    main()
