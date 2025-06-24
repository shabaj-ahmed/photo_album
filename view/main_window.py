import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox,
    QTextEdit, QMessageBox, QListWidget, QScrollArea, QGridLayout, QSplitter,
    QDateEdit, QInputDialog, QListWidgetItem
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate

from .widgets.editable_dropdown import EditableDropdown
from .widgets.toast import Toast
from .filter_panel import FilterPanel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Album App")
        self.setMinimumSize(800, 480)

        self.folder_path = ''
        self.image_list = []
        self.current_index = -1
        self.metadata_changed = False
        self.people_list = []
        self.group_list = []
        self.emotion_list = []

        self.db = None

        self.fetch_metadata = None
        self.load_folder_callback = None
        self.on_save_metadata = None
        self.on_apply_filters = None
        self.on_clear_filters = None

        self.setup_ui()

    def setup_ui(self):
        self.root_layout = QVBoxLayout()
        self.setLayout(self.root_layout)

        self.setup_header()
        self.filter_widget = FilterPanel(
            self.people_list,
            self.group_list,
            self.emotion_list,
            on_apply_filters=self.on_apply_filters,
            on_clear_filters=self.on_clear_filters
        )
        self.setup_metadata_panel()
        self.setup_image_panels()
        self.setup_splitter()
        self.setup_footer()

        # Initial splitter state
        self.filter_widget.hide()
        self.metadata_widget.hide()
        self.full_image_label.hide()
        self.splitter.setSizes([0, 1, 0])

    def setup_header(self):
        self.header_layout = QHBoxLayout()

        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.toggle_filter_panel)
        self.filter_button.hide()
        self.header_layout.addWidget(self.filter_button)

        self.metadata_button = QPushButton("Toggle Metadata")
        self.metadata_button.clicked.connect(self.toggle_metadata_panel)
        self.metadata_button.hide()
        self.header_layout.addWidget(self.metadata_button)

        self.back_button = QPushButton("Back to Grid")
        self.back_button.clicked.connect(self.display_grid_view)
        self.back_button.hide()
        self.header_layout.addWidget(self.back_button)

        self.header_layout.addStretch()
        self.root_layout.addLayout(self.header_layout)

    def setup_metadata_panel(self):
        self.metadata_panel = QVBoxLayout()

        self.metadata_panel.addWidget(QLabel("Description:"))
        self.description = QTextEdit()
        self.metadata_panel.addWidget(self.description)

        self.metadata_panel.addWidget(QLabel("Who is in the photo:"))
        self.people_list_widget = QListWidget()
        self.people_list_widget.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.people_list_widget)
        self.people_list_widget.itemClicked.connect(self.handle_person_click)

        self.metadata_panel.addWidget(QLabel("Group:"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.group_list_widget)
        self.group_list_widget.itemClicked.connect(self.handle_group_click)

        self.metadata_panel.addWidget(QLabel("Emotion:"))
        self.emotion_list_widget = QListWidget()
        self.emotion_list_widget.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.emotion_list_widget)
        self.emotion_list_widget.itemClicked.connect(self.handle_emotion_click)

        self.metadata_panel.addWidget(QLabel("Location:"))
        self.use_location_checkbox = QCheckBox("Specify Location")
        self.metadata_panel.addWidget(self.use_location_checkbox)
        self.name_dropdown = EditableDropdown(
            "name",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry(
                "name", val)
        )
        self.category_dropdown = EditableDropdown(
            "category",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry(
                "category", val)
        )
        self.country_dropdown = EditableDropdown(
            "country",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry(
                "country", val)
        )
        self.region_dropdown = EditableDropdown(
            "region",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry(
                "region", val)
        )
        self.city_dropdown = EditableDropdown(
            "city",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry(
                "city", val)
        )
        self.postcode_dropdown = EditableDropdown(
            "postcode",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry(
                "postcode", val)
        )

        # Add to layout
        self.location_container = QWidget()
        self.location_layout = QVBoxLayout()
        self.location_container.setLayout(self.location_layout)

        self.location_layout.addWidget(self.name_dropdown)
        self.location_layout.addWidget(self.category_dropdown)
        self.location_layout.addWidget(self.country_dropdown)
        self.location_layout.addWidget(self.region_dropdown)
        self.location_layout.addWidget(self.city_dropdown)
        self.location_layout.addWidget(self.postcode_dropdown)

        self.use_location_checkbox.stateChanged.connect(
            lambda state: self.location_container.setVisible(
                state == Qt.CheckState.Checked.value)
        )
        self.location_container.setVisible(False)  # Initially hidden

        self.metadata_panel.addWidget(self.location_container)

        self.metadata_panel.addWidget(QLabel("Date:"))
        self.use_metadata_date_checkbox = QCheckBox("Specify Date")
        self.metadata_panel.addWidget(self.use_metadata_date_checkbox)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate.currentDate())  # Default
        self.date.setEnabled(False)  # Initially disabled
        self.metadata_panel.addWidget(self.date)

        # Toggle enabling
        self.use_metadata_date_checkbox.stateChanged.connect(
            lambda state: self.date.setEnabled(
                state == Qt.CheckState.Checked.value)
        )

        self.save_button = QPushButton("Save Metadata")
        self.save_button.clicked.connect(
            lambda: self.on_save_metadata(
                self.collect_metadata()) if self.on_save_metadata else None
        )
        self.metadata_panel.addWidget(self.save_button)

        self.metadata_widget = QWidget()
        self.metadata_widget.setLayout(self.metadata_panel)

    def setup_image_panels(self):
        self.scroll_area = QScrollArea()
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.grid_widget)
        self.scroll_area.setWidgetResizable(True)

        self.full_image_panel = QVBoxLayout()
        self.full_image_widget = QWidget()
        self.full_image_widget.setLayout(self.full_image_panel)

        self.full_image_label = QLabel()
        self.full_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.full_image_panel.addWidget(self.full_image_label)

        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Prev")
        self.next_button = QPushButton("Next →")
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        self.prev_button.hide()
        self.next_button.hide()
        self.nav_layout.addWidget(self.prev_button)
        self.nav_layout.addWidget(self.next_button)

        self.full_image_panel.addLayout(self.nav_layout)

        # Combine both scroll and image views into a container
        self.main_view_layout = QVBoxLayout()
        self.main_view_widget = QWidget()
        self.main_view_widget.setLayout(self.main_view_layout)
        self.main_view_layout.addWidget(self.scroll_area)
        self.main_view_layout.addWidget(self.full_image_widget)

    def setup_splitter(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.filter_widget)
        self.splitter.addWidget(self.main_view_widget)
        self.splitter.addWidget(self.metadata_widget)
        self.root_layout.addWidget(self.splitter, stretch=1)

    def setup_footer(self):
        self.load_button = QPushButton("Load Folder")
        self.load_button.clicked.connect(
            lambda: self.load_folder_callback() if self.load_folder_callback else None
        )

        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.load_button)
        self.footer_layout.addStretch()

        self.footer_widget = QWidget()
        self.footer_widget.setLayout(self.footer_layout)
        self.root_layout.addWidget(self.footer_widget)

    def display_grid_view(self):
        self.clear_layout(self.grid_layout)
        self.splitter.show()
        self.scroll_area.show()
        self.full_image_label.hide()
        self.metadata_widget.hide()
        self.metadata_button.hide()
        self.back_button.hide()
        self.prev_button.hide()
        self.next_button.hide()

        self.update_splitter_sizes()

        for i, filename in enumerate(self.image_list):
            image_path = os.path.join(self.folder_path, filename)
            pixmap = QPixmap(image_path).scaledToWidth(
                200, Qt.TransformationMode.SmoothTransformation)
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
        pixmap = QPixmap(image_path).scaledToWidth(
            800, Qt.TransformationMode.SmoothTransformation)
        self.full_image_label.setPixmap(pixmap)
        self.scroll_area.hide()
        self.splitter.show()
        self.full_image_label.show()
        self.metadata_widget.show()
        self.metadata_button.show()
        self.back_button.show()
        self.prev_button.show()
        self.next_button.show()

        self.update_splitter_sizes()

        # Load from DB
        metadata = self.fetch_metadata(
            filename) if self.fetch_metadata else None
        if not metadata:
            return

        self.description.setPlainText(metadata["description"])
        if metadata["date"]:
            self.use_metadata_date_checkbox.setChecked(True)
            self.date.setEnabled(True)
            self.date.setDate(QDate.fromString(metadata["date"], "yyyy-MM-dd"))
        else:
            self.use_metadata_date_checkbox.setChecked(False)
            self.date.setEnabled(False)

        for i in range(self.people_list_widget.count()):
            item = self.people_list_widget.item(i)
            item.setSelected(item.text() in metadata["people"])

        for i in range(self.group_list_widget.count()):
            item = self.group_list_widget.item(i)
            item.setSelected(item.text() in metadata["groups"])

        for i in range(self.emotion_list_widget.count()):
            item = self.emotion_list_widget.item(i)
            item.setSelected(item.text() in metadata["emotions"])

        # Populate location fields if location is present
        location = metadata.get("location")
        if location:
            self.use_location_checkbox.setChecked(True)
            self.location_container.setVisible(True)

            self.name_dropdown.setCurrentText(location.get("name") or "")
            self.category_dropdown.setCurrentText(
                location.get("category") or "")
            self.country_dropdown.setCurrentText(location.get("country") or "")
            self.region_dropdown.setCurrentText(location.get("region") or "")
            self.city_dropdown.setCurrentText(location.get("city") or "")
            self.postcode_dropdown.setCurrentText(
                location.get("postcode") or "")
        else:
            self.use_location_checkbox.setChecked(False)
            self.location_container.setVisible(False)

            self.name_dropdown.setCurrentIndex(-1)
            self.category_dropdown.setCurrentIndex(-1)
            self.country_dropdown.setCurrentIndex(-1)
            self.region_dropdown.setCurrentIndex(-1)
            self.city_dropdown.setCurrentIndex(-1)
            self.postcode_dropdown.setCurrentIndex(-1)

    def next_image(self):
        if self.metadata_changed:
            QMessageBox.warning(self, "Unsaved Changes",
                                "Please save changes before navigating.")
            return
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_fullscreen_image(self.current_index)

    def prev_image(self):
        if self.metadata_changed:
            QMessageBox.warning(self, "Unsaved Changes",
                                "Please save changes before navigating.")
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.show_fullscreen_image(self.current_index)

    def toggle_filter_panel(self):
        if self.filter_widget.isVisible():
            self.filter_widget.hide()
        else:
            self.filter_widget.show()
        self.update_splitter_sizes()

    def toggle_metadata_panel(self):
        if self.metadata_widget.isVisible():
            self.metadata_widget.hide()
        else:
            self.metadata_widget.show()
        self.update_splitter_sizes()

    def update_splitter_sizes(self):
        left = 300 if self.filter_widget.isVisible() else 0
        right = 300 if self.metadata_widget.isVisible() else 0
        center = max(600, self.width() - left - right)
        self.splitter.setSizes([left, center, right])

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_people_list(self, people):
            self.people_list_widget.clear()
            for person in people:
                self.people_list_widget.addItem(QListWidgetItem(person))
            self.people_list_widget.addItem(QListWidgetItem("+ Add New..."))

    def handle_person_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(
                self, "Add Person", "Enter person's name:")
            if ok and name.strip():
                name = name.strip()
                current_people = [
                    self.people_list_widget.item(i).text()
                    # exclude "+ Add New..."
                    for i in range(self.people_list_widget.count() - 1)
                ]
                if name not in current_people:
                    current_people.append(name)
                    self.populate_people_list(
                        current_people)  # pass updated list
                    # Auto-select the newly added person
                    for i in range(self.people_list_widget.count()):
                        if self.people_list_widget.item(i).text() == name:
                            self.people_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True

    def populate_group_list(self, groups):
        self.group_list_widget.clear()
        for group in groups:
            self.group_list_widget.addItem(QListWidgetItem(group))
        self.group_list_widget.addItem(QListWidgetItem("+ Add New..."))

    def handle_group_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(
                self, "Add Group", "Enter group name:")
            if ok and name.strip():
                name = name.strip()
                current_groups = [
                    self.group_list_widget.item(i).text()
                    # exclude "+ Add New..."
                    for i in range(self.group_list_widget.count() - 1)
                ]
                if name not in current_groups:
                    current_groups.append(name)
                    self.populate_group_list(
                        current_groups)  # pass updated list
                    # Auto-select the newly added group
                    for i in range(self.group_list_widget.count()):
                        if self.group_list_widget.item(i).text() == name:
                            self.group_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True

    def populate_emotion_list(self, emotions):
        self.emotion_list_widget.clear()
        for emotion in emotions:
            self.emotion_list_widget.addItem(QListWidgetItem(emotion))
        self.emotion_list_widget.addItem(QListWidgetItem("+ Add New..."))

    def handle_emotion_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(
                self, "Add Emotion", "Enter emotion:")
            if ok and name.strip():
                name = name.strip()
                current_emotions = [
                    self.emotion_list_widget.item(i).text()
                    # exclude "+ Add New..."
                    for i in range(self.emotion_list_widget.count() - 1)
                ]
                if name not in current_emotions:
                    current_emotions.append(name)
                    self.populate_emotion_list(
                        current_emotions)  # pass updated list
                    # Auto-select the newly added emotion
                    for i in range(self.emotion_list_widget.count()):
                        if self.emotion_list_widget.item(i).text() == name:
                            self.emotion_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True

    def populate_location_list(self, widget, items):
        widget.clear()
        for value in sorted(set(items)):
            widget.addItem(QListWidgetItem(value))

    def collect_metadata(self):
        if 0 <= self.current_index < len(self.image_list):
            filename = self.image_list[self.current_index]
        else:
            filename = ""

        description = self.description.toPlainText()

        if self.use_metadata_date_checkbox.isChecked():
            date = self.date.date().toString("yyyy-MM-dd")
        else:
            date = ""

        selected_people = [
            item.text() for item in self.people_list_widget.selectedItems()
            if item.text() != "+ Add New..."
        ]

        selected_groups = [
            item.text() for item in self.group_list_widget.selectedItems()
            if item.text() != "+ Add New..."
        ]

        selected_emotions = [
            item.text() for item in self.emotion_list_widget.selectedItems()
            if item.text() != "+ Add New..."
        ]

        if self.use_location_checkbox.isChecked():
            location = {
                "name": self.name_dropdown.currentText().strip() or None,
                "category": self.category_dropdown.currentText().strip() or None,
                "country": self.country_dropdown.currentText().strip() or None,
                "region": self.region_dropdown.currentText().strip() or None,
                "city": self.city_dropdown.currentText().strip() or None,
                "postcode": self.postcode_dropdown.currentText().strip() or None
            }
        else:
            location = None

        Toast(self, "Metadata saved.")

        return {
            "filename": filename,
            "description": description,
            "people": selected_people,
            "groups": selected_groups,
            "emotions": selected_emotions,
            "location": location,
            "date": date
        }
