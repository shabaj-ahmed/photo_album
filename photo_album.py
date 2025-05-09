import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QCheckBox, QLineEdit, QTextEdit, QComboBox, QMessageBox,
    QListWidget, QListWidgetItem, QInputDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import exiftool
import json

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

        self.setup_ui()
    
    def setup_ui(self):
        # === Root Layout ===
        root_layout = QVBoxLayout()

        # === Header Layout ===
        header_layout = QHBoxLayout()

        # Filters (placeholder for now)

        # Show duplicates toggle (placeholder for now)

        # View selector
        # Zoom in/Out and automatically change from grid to single view

        # Spacer
        header_layout.addStretch()

        # Reset/clear all Filters button (placeholder for now)

        root_layout.addLayout(header_layout)

        # === Main Content Layout ===
        main_content_layout = QHBoxLayout()

        # === Left Panel: Image Display + Nav ===
        image_nav_layout = QVBoxLayout()

        # Image display
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_nav_layout.addWidget(self.image_label)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Folder")
        self.prev_button = QPushButton("← Prev")
        self.next_button = QPushButton("Next →")
        nav_layout.addWidget(self.load_button)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)

        image_nav_layout.addLayout(nav_layout)
        main_content_layout.addLayout(image_nav_layout, 7)  # 7/10 of width

        # === Right Panel: Metadata Editor ===
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Description:"))
        self.description = QTextEdit()
        form_layout.addWidget(self.description)

        form_layout.addWidget(QLabel("Who is in the photo:"))
        self.people_list_widget = QListWidget()
        self.people_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        form_layout.addWidget(self.people_list_widget)
        self.populate_people_list()
        self.people_list_widget.itemClicked.connect(self.handle_person_click)
        form_layout.addWidget(self.people_list_widget)

        form_layout.addWidget(QLabel("Group:"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        form_layout.addWidget(self.group_list_widget)
        self.populate_group_list()
        self.group_list_widget.itemClicked.connect(self.handle_group_click)
        form_layout.addWidget(self.group_list_widget)

        form_layout.addWidget(QLabel("Location:"))
        self.location = QLineEdit()
        form_layout.addWidget(self.location)

        form_layout.addWidget(QLabel("Date:"))
        self.date = QLineEdit()
        form_layout.addWidget(self.date)

        form_layout.addWidget(QLabel("Other Metadata:"))
        self.other_metadata = QTextEdit()
        form_layout.addWidget(self.other_metadata)

        # Save button
        self.save_button = QPushButton("Save Metadata")
        form_layout.addWidget(self.save_button)

        main_content_layout.addLayout(form_layout, 3)  # 3/10 of width

        # Add to root layout
        root_layout.addLayout(main_content_layout)

        self.setLayout(root_layout)

        # Connect buttons (no change)
        self.load_button.clicked.connect(self.load_folder)
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        self.save_button.clicked.connect(self.save_metadata)

        # Track changes
        self.description.textChanged.connect(self.mark_dirty)
        self.people_list_widget.itemChanged.connect(self.mark_dirty)
        self.group_list_widget.itemChanged.connect(self.mark_dirty)
        self.location.textChanged.connect(self.mark_dirty)
        self.date.textChanged.connect(self.mark_dirty)
        self.other_metadata.textChanged.connect(self.mark_dirty)

    def mark_dirty(self):
        self.metadata_changed = True
    
    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.folder_path = folder
            self.image_list = [f for f in os.listdir(folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
            self.current_index = 0
            self.load_image()
    
    def load_image(self):
        if self.metadata_changed:
            QMessageBox.warning(self, "Unsaved Changes", "Please save changes before navigating.")
            return

        if 0 <= self.current_index < len(self.image_list):
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            pixmap = QPixmap(image_path).scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.read_metadata(image_path)
    
    def read_metadata(self, image_path):
        with exiftool.ExifTool() as et:
            output = et.execute(b"-j", image_path.encode("utf-8"))
            metadata = json.loads(output)[0]

        self.description.setText(metadata.get('XMP:Description', ''))
        self.location.setText(metadata.get('XMP:Location', ''))
        self.date.setText(metadata.get('EXIF:DateTimeOriginal', ''))
        # Simplify other metadata display
        self.other_metadata.setText('\n'.join(f"{k}: {v}" for k, v in metadata.items()))
        self.metadata_changed = False
    
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

    def next_image(self):
        pass

    def prev_image(self):
        pass
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())