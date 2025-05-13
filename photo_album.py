import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QCheckBox, QLineEdit, QTextEdit, QMessageBox, QListWidget,
    QListWidgetItem, QInputDialog, QScrollArea, QGridLayout, QSplitter
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import sqlite3

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Album App")
        self.setMinimumSize(800, 480)

        self.folder_path = ''
        self.image_list = []
        self.current_index = -1
        self.metadata_changed = False
        self.people_list = ["Person 1", "Person 2", "Person 3"]  # Predefined people

        self.db = None
        self.filter_mode = False # Filter for displaying tagged or untagged images

        self.setup_ui()
    
    def setup_ui(self):
        # === Root Layout ===
        self.root_layout = QVBoxLayout()

        # === Header Layout ===
        self.header_layout = QHBoxLayout()

        # Filters (placeholder for now)
        self.filter_checkbox = QCheckBox("Filter by Tags")
        self.filter_checkbox.setChecked(self.filter_mode)
        self.filter_checkbox.stateChanged.connect(self.toggle_filter_mode)
        self.header_layout.addWidget(self.filter_checkbox)

        # Show duplicates toggle (placeholder for now)

        # View selector
        self.back_button = QPushButton("Back to Grid")
        self.back_button.clicked.connect(self.display_grid_view)
        self.back_button.hide()
        self.header_layout.addWidget(self.back_button)

        # Spacer
        self.header_layout.addStretch()

        # Reset/clear all Filters button (placeholder for now)

        self.root_layout.addLayout(self.header_layout)

        # === Main Content Layout ===
        self.main_content_layout = QHBoxLayout()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Image display
            ## Scrollable area for grid view
        self.scroll_area = QScrollArea()
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.grid_widget)
        self.scroll_area.setWidgetResizable(True)

            ## Full-screen view
        self.full_image_panel = QVBoxLayout()
        self.full_image_widget = QWidget()
        self.full_image_widget.setLayout(self.full_image_panel)
        self.full_image_label = QLabel()
        self.full_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.full_image_label.hide()
        self.full_image_panel.addWidget(self.full_image_label)

        # === Left Panel (grid view + nav bar) ===
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Prev")
        self.next_button = QPushButton("Next →")
        self.prev_button.hide()
        self.next_button.hide()
        self.nav_layout.addWidget(self.prev_button)
        self.nav_layout.addWidget(self.next_button)

        self.full_image_panel.addLayout(self.nav_layout)
        self.splitter.addWidget(self.full_image_widget)

        # === Right Panel: Metadata Editor ===
        self.metadata_panel = QVBoxLayout()
        self.metadata_panel.addWidget(QLabel("Description:"))
        self.description = QTextEdit()
        self.metadata_panel.addWidget(self.description)

        self.metadata_panel.addWidget(QLabel("Who is in the photo:"))
        self.people_list_widget = QListWidget()
        self.people_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.people_list_widget)
        self.populate_people_list()
        self.people_list_widget.itemClicked.connect(self.handle_person_click)
        self.metadata_panel.addWidget(self.people_list_widget)

        self.metadata_panel.addWidget(QLabel("Group:"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.group_list_widget)
        self.populate_group_list()
        self.group_list_widget.itemClicked.connect(self.handle_group_click)
        self.metadata_panel.addWidget(self.group_list_widget)

        self.metadata_panel.addWidget(QLabel("Location:"))
        self.location = QLineEdit()
        self.metadata_panel.addWidget(self.location)

        self.metadata_panel.addWidget(QLabel("Date:"))
        self.date = QLineEdit()
        self.metadata_panel.addWidget(self.date)

        # Save button
        self.save_button = QPushButton("Save Metadata")
        self.metadata_panel.addWidget(self.save_button)

        self.metadata_widget = QWidget()
        self.metadata_widget.setLayout(self.metadata_panel)
        self.metadata_widget.hide()  # Hide the form layout initially
        self.splitter.addWidget(self.metadata_widget)
        self.splitter.setSizes([7, 3])

        # Setup root layout
        self.root_layout.addWidget(self.scroll_area)
        self.root_layout.addWidget(self.splitter)

        self.load_button = QPushButton("Load Folder")
        self.root_layout.addWidget(self.load_button)

        self.setLayout(self.root_layout)

        # Connect buttons (no change)
        self.load_button.clicked.connect(self.load_folder)
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        self.save_button.clicked.connect(self.save_metadata)
    
    def toggle_filter_mode(self, state):
        self.filter_mode = bool(state)
        self.apply_filter()

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        self.load_button.hide() # Hide the load button after selecting a folder
        if folder:
            self.folder_path = folder
            self.init_db()
            self.scan_folder()
            self.apply_filter()
    
    def init_db(self):
        db_path = os.path.join(self.folder_path, "metadata.db")
        self.db = sqlite3.connect(db_path)
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ImageMetadata (
                id INTEGER PRIMARY KEY,
                filename TEXT UNIQUE,
                description TEXT,
                people TEXT,
                tagged INTEGER DEFAULT 0
            )
        """)
        self.db.commit()

    def apply_filter(self):
        cursor = self.db.cursor()
        if self.filter_mode:
            cursor.execute("SELECT filename FROM ImageMetadata WHERE tagged = 1")
        else:
            cursor.execute("SELECT filename FROM ImageMetadata WHERE tagged = 0")
        self.image_list = [row[0] for row in cursor.fetchall()]
        self.display_grid_view()
    
    def display_grid_view(self):
        self.clear_layout(self.grid_layout)
        self.scroll_area.show()
        self.splitter.hide()
        self.full_image_label.hide()
        self.metadata_widget.hide()
        self.back_button.hide()

        for i, filename in enumerate(self.image_list):
            image_path = os.path.join(self.folder_path, filename)
            pixmap = QPixmap(image_path).scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            thumb_label = QLabel()
            thumb_label.setPixmap(pixmap)

            # Wrap in a lambda to avoid late-binding bug
            def handler(event, idx=i):
                self.show_fullscreen_image(idx)
            thumb_label.mouseDoubleClickEvent = handler

            self.grid_layout.addWidget(thumb_label, i // 4, i % 4)
    
    def show_fullscreen_image(self, index):
        self.current_index = index
        filename = self.image_list[self.current_index]
        image_path = os.path.join(self.folder_path, filename)
        pixmap = QPixmap(image_path).scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
        self.full_image_label.setPixmap(pixmap)
        self.scroll_area.hide()
        self.splitter.show()
        self.full_image_label.show()
        self.metadata_widget.show()
        self.back_button.show()
        self.splitter.setSizes([7, 3])

        cursor = self.db.cursor()
        cursor.execute("SELECT description, people FROM ImageMetadata WHERE filename = ?", (filename,))
        row = cursor.fetchone()
        if row:
            self.description.setText(row[0] or '')
            people = row[1].split(',') if row[1] else []
            for i in range(self.people_list_widget.count()):
                item = self.people_list_widget.item(i)
                item.setSelected(item.text() in people)

    def scan_folder(self):
        cursor = self.db.cursor()
        for f in os.listdir(self.folder_path):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                cursor.execute("INSERT OR IGNORE INTO ImageMetadata (filename) VALUES (?)", (f,))
        self.db.commit()
    
    def populate_people_list(self):
        self.people_list_widget.clear()
        for person in self.people_list:
            item = QListWidgetItem(person)
            self.people_list_widget.addItem(item)

        # Add the "Add New..." item
        add_item = QListWidgetItem("+ Add New...")
        add_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Not selectable
        self.people_list_widget.addItem(add_item)
    
    def handle_person_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(self, "Add Person", "Enter person's name:")
            if ok and name.strip():
                name = name.strip()
                if name not in self.people_list:
                    self.people_list.append(name)
                    self.populate_people_list()
                    # Auto-select the newly added person
                    for i in range(self.people_list_widget.count()):
                        if self.people_list_widget.item(i).text() == name:
                            self.people_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True
    
    def populate_group_list(self):
        self.group_list_widget.clear()
        for group in ["Family", "Friend", "Work Group"]:  # You can later load from DB
            item = QListWidgetItem(group)
            self.group_list_widget.addItem(item)

        # Add New option
        add_item = QListWidgetItem("+ Add New...")
        add_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.group_list_widget.addItem(add_item)
    
    def handle_group_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(self, "Add Group", "Enter group name:")
            if ok and name.strip():
                name = name.strip()
                if name not in [self.group_list_widget.item(i).text() for i in range(self.group_list_widget.count())]:
                    self.populate_group_list()  # Rebuild list with new item
                    for i in range(self.group_list_widget.count()):
                        if self.group_list_widget.item(i).text() == name:
                            self.group_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True

    def save_metadata(self):
        pass
        # Display success message (How to toast in PyQt?)

    def next_image(self):
        if self.metadata_changed:
            QMessageBox.warning(self, "Unsaved Changes", "Please save changes before navigating.")
            return
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_fullscreen_image(self.current_index)

    def prev_image(self):
        if self.metadata_changed:
            QMessageBox.warning(self, "Unsaved Changes", "Please save changes before navigating.")
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.show_fullscreen_image(self.current_index)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())