# 📌 DCC Integration - Python Developer Assessment

A project integrating a Digital Content Creation (DCC) tool (Blender/Maya) with a local server, a SQLite inventory system, and a PyQt-based UI.

---

## 📋 Project Overview

This project connects a **DCC tool (Blender/Maya)** with a **Flask server**, managing **object transforms** and an **inventory system** using SQLite.  
It includes:
1. **A Blender Add-on** to send object transform data to the server.
2. **A Flask REST API** to store transform data and manage an inventory system.
3. **A PyQt UI** to display and modify inventory items.
4. **Asynchronous communication** to keep the UI responsive.

---

## 🏗 Project Structure

```
📂 dcc_integration/
 ├── 📜 dcc_plugin.py         # Blender/Maya Plugin
 ├── 📜 server.py             # Flask API Server
 ├── 📜 inventory_ui.py       # PyQt5 UI
 ├── 📜 requirements.txt      # Dependencies
 ├── 📜 README.md             # Documentation
 ├── 📜 inventory.db          # SQLite database (created automatically)
```

---

## ⚙️ Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/dcc-integration.git
cd dcc-integration
```

### Step 2: Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

_(If `requirements.txt` is missing, install manually)_

```bash
pip install Flask requests PyQt5
```

---

## 🚀 How to Run

### 1️⃣ Start the Flask Server

```bash
python server.py
```

- The server runs at `http://localhost:5000`
- It manages transforms and inventory with a **10-second artificial delay** for testing responsiveness.

### 2️⃣ Run the PyQt UI

```bash
python inventory_ui.py
```

- Displays the inventory.
- Allows purchasing/returning items.
- Keeps UI responsive using **QThreads**.

### 3️⃣ Install and Use the Blender Plugin

1. Open **Blender**.
2. Navigate to `Edit > Preferences > Add-ons > Install...`
3. Select `dcc_plugin.py` and enable the add-on.
4. In **3D Viewport**, select an object and modify its transform.
5. Use the **"DCC Plugin"** panel to send transform data to the server.

---

## 📡 API Endpoints

| Endpoint            | Method | Description |
|---------------------|--------|-------------|
| `/transform`       | POST   | Accepts position, rotation, scale data |
| `/translation`     | POST   | Accepts position data only |
| `/rotation`       | POST   | Accepts rotation data only |
| `/scale`          | POST   | Accepts scale data only |
| `/file-path`      | GET    | Returns the DCC file path |
| `/add-item`       | POST   | Adds an inventory item |
| `/remove-item`    | POST   | Removes an inventory item |
| `/update-quantity` | POST   | Updates an inventory item (now UPSERT) |
| `/inventory`      | GET    | Returns the full inventory |


## 📜 License

This project is licensed under the MIT License.
