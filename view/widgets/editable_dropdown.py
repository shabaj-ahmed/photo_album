from PyQt6.QtWidgets import (
    QComboBox, QInputDialog, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, QPoint


class EditableDropdown(QComboBox):
    def __init__(self, label, values=None, parent=None, remove_callback=None):
        super().__init__(parent)
        self.label = label
        self.remove_callback = remove_callback
        self.setEditable(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_deletion_menu)
        self.activated[int].connect(self.handle_index_change)

        self.add_items([])

    def add_items(self, items):
        self.clear()
        self.addItem(f"Select a {self.label}")
        self.addItems(sorted(set(items)))
        self.addItem("+ Add new...")
        self.setCurrentIndex(0)

    def handle_add_new(self):
        text, ok = QInputDialog.getText(
            self, f"Add new {self.label}", f"Enter new {self.label}:")
        if ok and text:
            text = text.strip()
            if text and self.findText(text) == -1:
                self.insertItem(self.count() - 1, text)
            self.setCurrentText(text)
        else:
            # Reset selection to default value if cancelled
            self.setCurrentIndex(0)

    def show_deletion_menu(self, pos: QPoint):
        current_text = self.currentText()

        # Do not show context menu if default name or "+ Add new..."
        if current_text == f"Select a {self.label}" or current_text == "+ Add new...":
            return
        
        menu = QMenu(self)
        remove_action = menu.addAction("Delete selected item")
        action = menu.exec(self.mapToGlobal(pos))
        if action == remove_action:
            self.remove_selected()

    def remove_selected(self):
        current_text = self.currentText()
        if current_text == f"Select a {self.label}" or current_text == "+ Add new...":
            return
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Remove '{current_text}' from {self.label} list?")
        if confirm == QMessageBox.StandardButton.Yes:
            index = self.findText(current_text)
            self.removeItem(index)
            if self.remove_callback:
                self.remove_callback(current_text)

    def handle_index_change(self, index):
        text = self.itemText(index)
        if text == "+ Add new...":
            self.handle_add_new()

    def get_selected_value(self):
        value = self.currentText().strip()
        if value == f"Select a {self.label}" or value == "+ Add new...":
            return None
        return value or None
