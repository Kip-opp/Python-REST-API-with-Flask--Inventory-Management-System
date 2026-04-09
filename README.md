# Inventory Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Flask REST API + CLI tool for managing inventory with Open Food Facts integration.

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://git@github.com:Kip-opp/Python-REST-API-with-Flask--Inventory-Management-System.git
   cd Python-REST-API-with-Flask--Inventory-Management-System.git
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify Flask installation:
   ```bash
   pip show flask
   ```

## Running the Application

### Terminal 1: Start the Flask Server
```bash
python run.py
```
You should see output indicating the server is running on `http://127.0.0.1:5000` with debug mode enabled.

### Terminal 2: Use the CLI Tool
Open a new terminal window and navigate to the project directory:
```bash
cd inventory-management-system-API
source venv/bin/activate  # Activate the same virtual environment
```

Now you can run CLI commands while the server runs in Terminal 1:

```bash
# List all inventory items
python cli_tool.py list

# Show a specific item by ID
python cli_tool.py show 1

# Search Open Food Facts API by barcode
python cli_tool.py find-api --barcode 3017624010701

# Add a new item manually
python cli_tool.py add --name "Oats" --brand "Quaker" --barcode "030000057698" --price 250 --stock 10

# Update an existing item
python cli_tool.py update 1 --price 400

# Delete an item
python cli_tool.py delete 1

# Search by product name
python cli_tool.py find-api --name "almond milk"

# Import from Open Food Facts into inventory
python cli_tool.py import-api --barcode 3017624010701 --price 300 --stock 10
```

### Terminal 3: Run Tests (Optional)
Open another terminal for testing:
```bash
cd inventory-management-system-API
source venv/bin/activate
python -m pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /inventory | Retrieve all inventory items |
| GET | /inventory/\<id\> | Retrieve a single item by ID |
| POST | /inventory | Create a new inventory item |
| PATCH | /inventory/\<id\> | Update an existing item |
| DELETE | /inventory/\<id\> | Remove an item from inventory |
| GET | /external/product?barcode=... | Search Open Food Facts by barcode |
| GET | /external/product?name=... | Search Open Food Facts by product name |
| POST | /external/product/import | Import product data from API into inventory |

## Input Validation

The API now includes comprehensive input validation for all endpoints:

- **Required Fields**: `name` is required when creating items
- **Data Types**: Price must be a number, stock must be an integer
- **Constraints**: Price and stock must be non-negative; nutriscore must be a-e or empty
- **Sanitization**: String fields are trimmed of whitespace

Validation errors return a 400 status with detailed error messages.

## Project Structure

```
inventory-management-system-API/
├── app/
│   ├── __init__.py          # Flask app factory
│   └── routes.py            # API route definitions
├── external/
│   ├── __init__.py
│   └── openfoodfacts.py     # Open Food Facts API client
├── tests/
│   ├── __init__.py
│   ├── test_routes.py       # API route tests
│   ├── test_external.py     # External API tests
│   └── test_cli.py          # CLI functionality tests
├── cli_tool.py              # Command-line interface
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This documentation
```

## Architecture Notes

- **App Factory Pattern**: The application uses a factory pattern in `app/__init__.py` to create the Flask app instance, enabling better testability and configuration management.
- **Separation of Concerns**: Routes are defined in `app/routes.py`, external API logic in `external/openfoodfacts.py`, and CLI commands in `cli_tool.py`.
- **Input Validation**: All API endpoints validate input data types and constraints (e.g., non-negative prices, valid nutriscore grades) with detailed error messages.
- **Thread-Safe ID Generation**: Item IDs are generated using a thread-safe counter to prevent race conditions in concurrent requests.
- **Testing**: Comprehensive unit tests with mocked external dependencies ensure reliable functionality without requiring internet connectivity.
- **Error Handling**: Proper HTTP status codes, detailed error messages, and improved CLI error reporting for better user experience.