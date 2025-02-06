import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableView, QPushButton, QHBoxLayout,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import (
    QAbstractTableModel, Qt, pyqtSignal, QObject, QThread
)

SERVER_URL = "http://localhost:5000"


# ---------------------------
# Inventory Model
# ---------------------------
class InventoryModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self.inventory = data if data is not None else []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self.inventory[index.row()][index.column()])

    def rowCount(self, index):
        return len(self.inventory)

    def columnCount(self, index):
        return 2  # Name and Quantity

    def headerData(self, section, orientation, role):
        headers = ["Name", "Quantity"]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return headers[section]

    def update_data(self, data):
        self.beginResetModel()
        self.inventory = data
        self.endResetModel()


# ---------------------------
# Worker to Fetch Inventory
# ---------------------------
class InventoryFetcher(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            response = requests.get(f"{SERVER_URL}/inventory")
            response.raise_for_status()
            data = response.json().get("inventory", [])
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------
# Worker to Update Quantity
# ---------------------------
class QuantityUpdater(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, item_name, delta, current_quantity):
        super().__init__()
        self.item_name = item_name
        self.delta = delta
        self.current_quantity = current_quantity

    def run(self):
        new_quantity = self.current_quantity + self.delta
        payload = {"name": self.item_name, "quantity": new_quantity}
        try:
            response = requests.post(f"{SERVER_URL}/update-quantity", json=payload)
            response.raise_for_status()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------
# Main UI Class
# ---------------------------
class InventoryUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory UI")
        self.resize(400, 300)
        layout = QVBoxLayout(self)

        # Table view to display inventory
        self.table = QTableView()
        self.model = InventoryModel()
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        # Buttons for purchase and return
        button_layout = QHBoxLayout()
        self.purchase_button = QPushButton("Purchase")
        self.return_button = QPushButton("Return")
        button_layout.addWidget(self.purchase_button)
        button_layout.addWidget(self.return_button)
        layout.addLayout(button_layout)

        # Connect buttons to their respective slots
        self.purchase_button.clicked.connect(self.purchase_item)
        self.return_button.clicked.connect(self.return_item)

        # Fetch inventory initially
        self.refresh_inventory()

    def refresh_inventory(self):
        # Use a QThread to fetch inventory without blocking the UI
        self.thread = QThread()
        self.worker = InventoryFetcher()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_inventory_fetched)
        self.worker.error.connect(self.on_error)
        # Clean up thread after work is finished
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_inventory_fetched(self, data):
        # Update the model with the fetched data
        self.model.update_data(data)

    def on_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def purchase_item(self):
        # Ask the user for the item name
        item_name, ok = QInputDialog.getText(self, "Purchase Item", "Item name:")
        if ok and item_name:
            current_quantity = self.get_current_quantity(item_name)
            self.update_quantity(item_name, -1, current_quantity)

    def return_item(self):
        # Ask the user for the item name
        item_name, ok = QInputDialog.getText(self, "Return Item", "Item name:")
        if ok and item_name:
            current_quantity = self.get_current_quantity(item_name)
            self.update_quantity(item_name, 1, current_quantity)

    def get_current_quantity(self, item_name):
        # Find the current quantity from the model
        current_quantity = 0
        for row in self.model.inventory:
            if row[0] == item_name:
                current_quantity = row[1]
                break
        return current_quantity

    def update_quantity(self, item_name, delta, current_quantity):
        # Use a QThread to update quantity without blocking the UI
        self.thread_update = QThread()
        self.updater = QuantityUpdater(item_name, delta, current_quantity)
        self.updater.moveToThread(self.thread_update)
        self.thread_update.started.connect(self.updater.run)
        self.updater.finished.connect(self.on_quantity_updated)
        self.updater.error.connect(self.on_error)
        self.updater.finished.connect(self.thread_update.quit)
        self.updater.finished.connect(self.updater.deleteLater)
        self.thread_update.finished.connect(self.thread_update.deleteLater)
        self.thread_update.start()

    def on_quantity_updated(self):
        # After updating quantity, refresh the inventory display
        self.refresh_inventory()


# ---------------------------
# Main Application Entry
# ---------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryUI()
    window.show()
    sys.exit(app.exec_())
