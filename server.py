import time
import sqlite3
import logging
from flask import Flask, request, jsonify, abort

# Initialize Flask application
app = Flask(__name__)

# Configure logging to output to the console at the INFO level
logging.basicConfig(level=logging.INFO)

# Define the SQLite database file
DATABASE = 'inventory.db'

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def delayed_response():
    """Apply an artificial 10-second delay to every response."""
    time.sleep(10)

def get_db_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # allow accessing columns by name if needed
    return conn

def init_db():
    """Create the inventory table if it does not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            name TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database on startup
init_db()

# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------

@app.route('/transform', methods=['POST'])
def transform():
    """
    Accepts transform data (position, rotation, scale) for an object.
    Expected JSON keys: "position", "rotation", "scale"
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /transform request with data: {data}")

    # Verify that all required transform keys are provided
    required_keys = ("position", "rotation", "scale")
    if not data or not all(key in data for key in required_keys):
        abort(400, description="Missing transform data. Expecting position, rotation, and scale.")

    return jsonify({"status": "success", "data": data}), 200

@app.route('/translation', methods=['POST'])
def translation():
    """
    Accepts position data only.
    Expected JSON key: "position"
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /translation request with data: {data}")

    if not data or "position" not in data:
        abort(400, description="Missing position data.")
    
    return jsonify({"status": "success", "position": data["position"]}), 200

@app.route('/rotation', methods=['POST'])
def rotation():
    """
    Accepts rotation data only.
    Expected JSON key: "rotation"
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /rotation request with data: {data}")

    if not data or "rotation" not in data:
        abort(400, description="Missing rotation data.")
    
    return jsonify({"status": "success", "rotation": data["rotation"]}), 200

@app.route('/scale', methods=['POST'])
def scale():
    """
    Accepts scale data only.
    Expected JSON key: "scale"
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /scale request with data: {data}")

    if not data or "scale" not in data:
        abort(400, description="Missing scale data.")
    
    return jsonify({"status": "success", "scale": data["scale"]}), 200

@app.route('/file-path', methods=['GET'])
def file_path():
    """
    Returns the DCC file's path.
    If the query parameter `?projectpath=true` is provided, returns the project folder path.
    """
    delayed_response()
    # Check if projectpath is requested
    projectpath = request.args.get('projectpath', 'false').lower() == 'true'
    logging.info(f"Received /file-path request. projectpath: {projectpath}")

    # Return dummy paths for demonstration purposes
    if projectpath:
        path = "/path/to/dcc/project/folder"
    else:
        path = "/path/to/dcc/file.blend"
    
    return jsonify({"status": "success", "file_path": path}), 200

@app.route('/add-item', methods=['POST'])
def add_item():
    """
    Adds an item to the inventory database.
    Expects JSON with keys: "name" and "quantity".
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /add-item request with data: {data}")

    if not data or "name" not in data or "quantity" not in data:
        abort(400, description="Missing item name or quantity.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO inventory (name, quantity) VALUES (?, ?)",
                       (data["name"], data["quantity"]))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        abort(400, description="Item already exists.")
    conn.close()
    return jsonify({"status": "success", "item": data}), 200

@app.route('/remove-item', methods=['POST'])
def remove_item():
    """
    Removes an item from the inventory database.
    Expects JSON with key: "name".
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /remove-item request with data: {data}")

    if not data or "name" not in data:
        abort(400, description="Missing item name.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (data["name"],))
    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Item not found.")
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "removed": data["name"]}), 200

@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    """
    Updates an item's quantity in the inventory.
    Expects JSON with keys: "name" and "quantity" (the new quantity).
    If the item does not exist, it will be inserted.
    """
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /update-quantity request with data: {data}")

    if not data or "name" not in data or "quantity" not in data:
        abort(400, description="Missing item name or quantity.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Perform an UPSERT: if the item exists, update its quantity;
        # if not, insert a new record.
        cursor.execute("""
            INSERT INTO inventory (name, quantity)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET quantity=excluded.quantity
        """, (data["name"], data["quantity"]))
        conn.commit()
    except Exception as e:
        conn.close()
        abort(400, description=str(e))
    conn.close()
    return jsonify({"status": "success", "updated": data}), 200

@app.route('/inventory', methods=['GET'])
def inventory():
    """
    Returns the full inventory as a list of items.
    Each item is represented as a pair [name, quantity].
    """
    delayed_response()
    logging.info("Received /inventory request")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity FROM inventory")
    items = cursor.fetchall()
    conn.close()

    # Convert rows to a list of lists for JSON serialization
    inventory_list = [list(item) for item in items]

    return jsonify({"status": "success", "inventory": inventory_list}), 200

# ----------------------------------------------------------------------
# Run the Server
# ----------------------------------------------------------------------

if __name__ == '__main__':
    # Run the Flask development server on port 5000
    app.run(debug=True)
