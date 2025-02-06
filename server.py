import time
import sqlite3
import logging
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Set up logging to output all requests
logging.basicConfig(level=logging.INFO)

DATABASE = 'inventory.db'

# Helper: Initialize SQLite database if not exists
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            name TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Utility: Artificial delay for all endpoints
def delayed_response():
    time.sleep(10)

# Endpoint: /transform
@app.route('/transform', methods=['POST'])
def transform():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /transform request with data: {data}")
    if not data or not all(k in data for k in ("position", "rotation", "scale")):
        abort(400, description="Missing transform data.")
    return jsonify({"status": "success", "data": data}), 200

# Endpoint: /translation
@app.route('/translation', methods=['POST'])
def translation():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /translation request with data: {data}")
    if not data or "position" not in data:
        abort(400, description="Missing position data.")
    return jsonify({"status": "success", "position": data["position"]}), 200

# Endpoint: /rotation
@app.route('/rotation', methods=['POST'])
def rotation():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /rotation request with data: {data}")
    if not data or "rotation" not in data:
        abort(400, description="Missing rotation data.")
    return jsonify({"status": "success", "rotation": data["rotation"]}), 200

# Endpoint: /scale
@app.route('/scale', methods=['POST'])
def scale():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /scale request with data: {data}")
    if not data or "scale" not in data:
        abort(400, description="Missing scale data.")
    return jsonify({"status": "success", "scale": data["scale"]}), 200

# Endpoint: /file-path
@app.route('/file-path', methods=['GET'])
def file_path():
    delayed_response()
    projectpath = request.args.get('projectpath', 'false').lower() == 'true'
    logging.info(f"Received /file-path request. projectpath: {projectpath}")
    # For demo purposes, we return a dummy path.
    if projectpath:
        path = "/path/to/blender/project/folder"
    else:
        path = "/path/to/blender/file.blend"
    return jsonify({"status": "success", "file_path": path}), 200

# Endpoint: /add-item
@app.route('/add-item', methods=['POST'])
def add_item():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /add-item request with data: {data}")
    if not data or "name" not in data or "quantity" not in data:
        abort(400, description="Missing item name or quantity.")
    
    conn = sqlite3.connect(DATABASE)
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

# Endpoint: /remove-item
@app.route('/remove-item', methods=['POST'])
def remove_item():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /remove-item request with data: {data}")
    if not data or "name" not in data:
        abort(400, description="Missing item name.")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (data["name"],))
    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Item not found.")
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "removed": data["name"]}), 200

# Endpoint: /update-quantity
@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    delayed_response()
    data = request.get_json()
    logging.info(f"Received /update-quantity request with data: {data}")
    if not data or "name" not in data or "quantity" not in data:
        abort(400, description="Missing item name or quantity.")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET quantity = ? WHERE name = ?", (data["quantity"], data["name"]))
    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Item not found.")
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "updated": data}), 200

if __name__ == '__main__':
    # Run on port 5000 (or your desired port)
    app.run(debug=True)
