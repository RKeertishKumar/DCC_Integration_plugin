import sys
import json
import threading
import requests
from PyQt5 import QtWidgets, QtCore

SERVER_URL = "http://localhost:5000"

class InventoryModel(QtCore.QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self.inventory = data if data is not None else []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.inventory[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.inventory)

    def columnCount(self, index):
        return 2  # name and quantity

    def headerData(self, section, orientation, role):
        headers = ["Name", "Quantity"]
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return headers[section]

    def update_data(self, data):
        self.beginResetModel()
        self.inventory = data
        self.endResetModel()

class InventoryUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory UI")
        self.resize(400, 300)
        self.layout = QtWidgets.QVBoxLayout(self)

        # Table view to display inventory
        self.table = QtWidgets.QTableView()
        self.model = InventoryModel()
        self.table.setModel(self.model)
        self.layout.addWidget(self.table)

        # Buttons for purchase and return
        button_layout = QtWidgets.QHBoxLayout()
        self.purchase_button = QtWidgets.QPushButton("Purchase")
        self.return_button = QtWidgets.QPushButton("Return")
        button_layout.addWidget(self.purchase_button)
        button_layout.addWidget(self.return_button)
        self.layout.addLayout(button_layout)

        # Connect buttons to their methods
        self.purchase_button.clicked.connect(self.purchase_item)
        self.return_button.clicked.connect(self.return_item)

        # Refresh the inventory on startup
        self.refresh_inventory()

    def refresh_inventory(self):
        # Run in a separate thread so the UI stays responsive
        threading.Thread(target=self._fetch_inventory, daemon=True).start()

    def _fetch_inventory(self):
        try:
            # For demo purposes, assume we have a server endpoint to get the full inventory.
            # If not available, you might directly query the SQLite database.
            # Here, we simulate a request.
            # In our example, we'll assume the server has an endpoint `/inventory` that returns all items.
            # For now, we fake a response.
            # Replace the following with an actual API call if implemented.
            # response = requests.get(f"{SERVER_URL}/inventory")
            # data = response.json().get("inventory", [])
            data = []  # Replace with actual server call if available.
            # For demo, let’s read from a local file or simply assign empty data.
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            data = []
        # Update the table model on the main thread
        QtCore.QMetaObject.invokeMethod(self, "update_table",
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(list, data))

    @QtCore.pyqtSlot(list)
    def update_table(self, data):
        self.model.update_data(data)

    def purchase_item(self):
        # For demonstration, we ask for an item name and decrease quantity by 1.
        item_name, ok = QtWidgets.QInputDialog.getText(self, "Purchase Item", "Item name:")
        if ok and item_name:
            # In a real app, you might call the server's /update-quantity endpoint.
            threading.Thread(target=self._update_quantity, args=(item_name, -1), daemon=True).start()

    def return_item(self):
        # For demonstration, we ask for an item name and increase quantity by 1.
        item_name, ok = QtWidgets.QInputDialog.getText(self, "Return Item", "Item name:")
        if ok and item_name:
            threading.Thread(target=self._update_quantity, args=(item_name, 1), daemon=True).start()

    def _update_quantity(self, item_name, delta):
        # This function calls the server to update quantity.
        # First, fetch the current quantity (this example assumes you can get it from your UI model).
        current_quantity = 0
        for row in self.model.inventory:
            if row[0] == item_name:
                current_quantity = row[1]
                break
        new_quantity = current_quantity + delta
        payload = {"name": item_name, "quantity": new_quantity}
        try:
            response = requests.post(f"{SERVER_URL}/update-quantity", json=payload)
            if response.status_code == 200:
                print(f"Quantity updated for {item_name}")
            else:
                print(f"Failed to update quantity: {response.text}")
        except Exception as e:
            print(f"Error during update: {e}")
        # Refresh inventory after update
        self.refresh_inventory()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = InventoryUI()
    window.show()
    sys.exit(app.exec_())
