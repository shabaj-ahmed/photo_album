import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QCheckBox, QLineEdit, QTextEdit, QMessageBox, QListWidget,
    QListWidgetItem, QInputDialog, QScrollArea, QGridLayout, QSplitter, QDateEdit
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, QPoint, QDate

from database import DatabaseManager

from widgets.editable_dropdown import EditableDropdown

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
        # self.filter_mode = False # Filter for displaying tagged or untagged images

        self.setup_ui()

    def setup_ui(self):
        self.root_layout = QVBoxLayout()
        self.setLayout(self.root_layout)

        self.setup_header()
        self.setup_filter_panel()
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

    def setup_filter_panel(self):
        self.filter_panel = QVBoxLayout()

        # Tagged status
        self.filter_panel.addWidget(QLabel("Filter by Tagged Status:"))
        self.untagged_checkbox = QCheckBox("Show Only Untagged Images")
        self.filter_panel.addWidget(self.untagged_checkbox)

        # People
        self.filter_panel.addWidget(QLabel("Filter by People:"))
        self.people_filter_list = QListWidget()
        self.people_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.people_filter_list)
        self.populate_people_filter_list()

        # Group
        self.filter_panel.addWidget(QLabel("Filter by Group:"))
        self.group_filter_list = QListWidget()
        self.group_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.group_filter_list)
        self.populate_group_filter_list()

        # Emotion
        self.filter_panel.addWidget(QLabel("Filter by Emotion:"))
        self.emotion_filter_list = QListWidget()
        self.emotion_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.emotion_filter_list)
        self.populate_emotion_filter_list()

        # Location
        label = QLabel("Filter by location name:")
        self.location_name_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.location_name_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.location_name_filter_list)

        label = QLabel("Filter by Category:")
        self.category_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.category_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.category_filter_list)

        label = QLabel("Filter by Region:")
        self.region_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.region_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.region_filter_list)

        label = QLabel("Filter by City:")
        self.city_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.city_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.city_filter_list)

        label = QLabel("Filter by Country:")
        self.country_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.country_filter_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.country_filter_list)

        self.populate_location_filters()

        # Date
        self.use_date_checkbox = QCheckBox("Filter by Date")
        self.filter_panel.addWidget(self.use_date_checkbox)

        self.date_filter_input = QDateEdit()
        self.date_filter_input.setCalendarPopup(True)
        self.date_filter_input.setDisplayFormat("yyyy-MM-dd")
        self.date_filter_input.setDate(QDate.currentDate())
        self.filter_panel.addWidget(self.date_filter_input)

        # Optional: disable date input by default
        self.date_filter_input.setEnabled(False)

        self.use_date_checkbox.stateChanged.connect(
            lambda state: self.date_filter_input.setEnabled(state == Qt.CheckState.Checked.value)
        )

        # Filter controls
        self.reset_filter_button = QPushButton("Clear Filters")
        self.reset_filter_button.clicked.connect(self.clear_filters)
        self.filter_panel.addWidget(self.reset_filter_button)

        self.apply_filter_button = QPushButton("Apply Filters")
        self.apply_filter_button.clicked.connect(self.apply_filters)
        self.filter_panel.addWidget(self.apply_filter_button)

        self.filter_widget = QWidget()
        self.filter_widget.setLayout(self.filter_panel)

    def populate_location_filters(self):
        if self.db:
            self.populate_list(self.location_name_filter_list, self.db.get_all_location_names())
            self.populate_list(self.category_filter_list, self.db.get_all_location_categories())
            self.populate_list(self.region_filter_list, self.db.get_all_location_regions())
            self.populate_list(self.city_filter_list, self.db.get_all_location_cities())
            self.populate_list(self.country_filter_list, self.db.get_all_location_countries())

    def populate_list(self, widget, items):
        widget.clear()
        for value in sorted(set(items)):
            widget.addItem(QListWidgetItem(value))

    def setup_metadata_panel(self):
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

        self.metadata_panel.addWidget(QLabel("Group:"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.group_list_widget)
        self.populate_group_list()
        self.group_list_widget.itemClicked.connect(self.handle_group_click)

        self.metadata_panel.addWidget(QLabel("Emotion:"))
        self.emotion_list_widget = QListWidget()
        self.emotion_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.metadata_panel.addWidget(self.emotion_list_widget)
        self.populate_emotion_list()
        self.emotion_list_widget.itemClicked.connect(self.handle_emotion_click)

        self.metadata_panel.addWidget(QLabel("Location:"))
        self.use_location_checkbox = QCheckBox("Specify Location")
        self.metadata_panel.addWidget(self.use_location_checkbox)
        self.name_dropdown = EditableDropdown(
            "name",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry("name", val)
        )
        self.category_dropdown = EditableDropdown(
            "category",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry("category", val)
        )
        self.country_dropdown = EditableDropdown(
            "country",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry("country", val)
        )
        self.region_dropdown = EditableDropdown(
            "region",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry("region", val)
        )
        self.city_dropdown = EditableDropdown(
            "city",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry("city", val)
        )
        self.postcode_dropdown = EditableDropdown(
            "postcode",
            values=[],  # populated after DB init
            remove_callback=lambda val: self.db.delete_location_entry("postcode", val)
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
            lambda state: self.location_container.setVisible(state == Qt.CheckState.Checked.value)
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
            lambda state: self.date.setEnabled(state == Qt.CheckState.Checked.value)
        )

        self.save_button = QPushButton("Save Metadata")
        self.save_button.clicked.connect(self.save_metadata)
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
        self.load_button.clicked.connect(self.load_folder)

        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.load_button)
        self.footer_layout.addStretch()

        self.footer_widget = QWidget()
        self.footer_widget.setLayout(self.footer_layout)
        self.root_layout.addWidget(self.footer_widget)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        self.load_button.hide() # Hide the load button after selecting a folder
        if folder:
            self.folder_path = folder
            self.init_db()
            self.scan_folder()
            self.populate_location_filters()
            self.populate_location_dropdowns()
            self.footer_widget.hide()
            self.filter_button.show()
    
    def init_db(self):
        db_path = os.path.join(self.folder_path, "metadata.db")
        self.db = DatabaseManager(db_path)
    
    def populate_location_dropdowns(self):
        self.category_dropdown.add_items(self.db.get_all_location_categories())
        self.country_dropdown.add_items(self.db.get_all_location_countries())
        self.region_dropdown.add_items(self.db.get_all_location_regions())
        self.city_dropdown.add_items(self.db.get_all_location_cities())
        self.postcode_dropdown.add_items(self.db.get_all_location_postcodes())
        self.name_dropdown.add_items(self.db.get_all_location_names())
    
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
        self.metadata_button.show()
        self.back_button.show()
        self.prev_button.show()
        self.next_button.show()

        self.update_splitter_sizes()

        # Load from DB
        metadata = self.db.load_image_metadata(filename)

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
            self.category_dropdown.setCurrentText(location.get("category") or "")
            self.country_dropdown.setCurrentText(location.get("country") or "")
            self.region_dropdown.setCurrentText(location.get("region") or "")
            self.city_dropdown.setCurrentText(location.get("city") or "")
            self.postcode_dropdown.setCurrentText(location.get("postcode") or "")
        else:
            self.use_location_checkbox.setChecked(False)
            self.location_container.setVisible(False)

            self.name_dropdown.setCurrentIndex(-1)
            self.category_dropdown.setCurrentIndex(-1)
            self.country_dropdown.setCurrentIndex(-1)
            self.region_dropdown.setCurrentIndex(-1)
            self.city_dropdown.setCurrentIndex(-1)
            self.postcode_dropdown.setCurrentIndex(-1)


    def scan_folder(self):
        # Get all image files from the folder
        image_extensions = (".jpg", ".jpeg", ".png", ".raw", ".heif", ".cr2", ".cr3", ".arw", ".tiff")
        files_in_folder = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith(image_extensions)
        ]

        self.image_list = []  # Reset image list

        self.image_list = self.db.insert_images_if_missing(files_in_folder)

        self.display_grid_view()
        
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

    def populate_emotion_list(self):
        self.emotion_list_widget.clear()
        for emotion in ["Happy", "Sad", "Excited", "Nostalgic"]:  # Example values
            item = QListWidgetItem(emotion)
            self.emotion_list_widget.addItem(item)

        add_item = QListWidgetItem("+ Add New...")
        add_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.emotion_list_widget.addItem(add_item)

    def handle_emotion_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(self, "Add Emotion", "Enter emotion:")
            if ok and name.strip():
                name = name.strip()
                if name not in [self.emotion_list_widget.item(i).text() for i in range(self.emotion_list_widget.count())]:
                    self.populate_emotion_list()
                    for i in range(self.emotion_list_widget.count()):
                        if self.emotion_list_widget.item(i).text() == name:
                            self.emotion_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True

    def save_metadata(self):
        if 0 <= self.current_index < len(self.image_list):
            filename = self.image_list[self.current_index]
            description = self.description.toPlainText()
            if self.use_metadata_date_checkbox.isChecked():
                date = self.date.date().toString("yyyy-MM-dd")
            else:
                date = ""

            # Get selected people
            selected_people = [
                item.text() for item in self.people_list_widget.selectedItems()
                if item.text() != "+ Add New..."
            ]

            # Get selected groups
            selected_groups = [
                item.text() for item in self.group_list_widget.selectedItems()
                if item.text() != "+ Add New..."
            ]

            # Get selected emotions
            selected_emotions = [
                item.text() for item in self.emotion_list_widget.selectedItems()
                if item.text() != "+ Add New..."
            ]

            # Build location dict only if location is enabled
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
            
            # Save everything to the database
            self.db.save_metadata(
                filename=filename,
                description=description,
                people=selected_people,
                groups=selected_groups,
                emotions=selected_emotions,
                location=location,
                date=date
            )

            self.populate_location_filters()

            self.show_toast("Metadata saved.")
            self.metadata_changed = False

    def show_toast(self, message, duration=2000):
        toast = QLabel(message, self)
        toast.setStyleSheet("""
            QLabel {
                background-color: #323232;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        toast.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        toast.adjustSize()

        # Calculate center position relative to window geometry on screen
        center_x = (self.width() - toast.width()) // 2
        center_y = (self.height() - toast.height()) // 2
        global_pos = self.mapToGlobal(QPoint(center_x, center_y))
        toast.move(global_pos)
        toast.show()

        # Fade out animation
        animation = QPropertyAnimation(toast, b"windowOpacity")
        animation.setDuration(1000)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

        animation.finished.connect(toast.deleteLater)
        QTimer.singleShot(duration, toast.close)

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

    def toggle_filter_panel(self):
        if self.filter_widget.isVisible():
            self.filter_widget.hide()
        else:
            self.populate_location_filters()
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

    def populate_people_filter_list(self):
        self.people_filter_list.clear()
        for person in self.people_list:
            item = QListWidgetItem(person)
            self.people_filter_list.addItem(item)

    def populate_group_filter_list(self):
        self.group_filter_list.clear()
        for group in ["Family", "Friend", "Work Group"]:
            item = QListWidgetItem(group)
            self.group_filter_list.addItem(item)

    def populate_emotion_filter_list(self):
        self.emotion_filter_list.clear()
        for emotion in ["Happy", "Sad", "Excited", "Nostalgic"]:
            item = QListWidgetItem(emotion)
            self.emotion_filter_list.addItem(item)

    def apply_filters(self):
        only_untagged = self.untagged_checkbox.isChecked()
        selected_people = [item.text() for item in self.people_filter_list.selectedItems()]
        selected_groups = [item.text() for item in self.group_filter_list.selectedItems()]
        selected_emotions = [item.text() for item in self.emotion_filter_list.selectedItems()]
        location_name = [item.text() for item in self.location_name_filter_list.selectedItems()]
        location_category = [item.text() for item in self.category_filter_list.selectedItems()]
        location_region = [item.text() for item in self.region_filter_list.selectedItems()]
        location_city = [item.text() for item in self.city_filter_list.selectedItems()]
        location_country = [item.text() for item in self.country_filter_list.selectedItems()]
        
        # Gather selected values for each location field
        location_name = [item.text() for item in self.location_name_filter_list.selectedItems()]
        location_category = [item.text() for item in self.category_filter_list.selectedItems()]
        location_region = [item.text() for item in self.region_filter_list.selectedItems()]
        location_city = [item.text() for item in self.city_filter_list.selectedItems()]
        location_country = [item.text() for item in self.country_filter_list.selectedItems()]

        # Only build the dictionary if there is at least one selection
        if any([location_name, location_category, location_region, location_city, location_country]):
            location = {}
            if location_name:
                location["name"] = location_name
            if location_category:
                location["category"] = location_category
            if location_region:
                location["region"] = location_region
            if location_city:
                location["city"] = location_city
            if location_country:
                location["country"] = location_country
        else:
            location = None
        
        print("FILTER DEBUG", location)

        date = self.date_filter_input.date().toString("yyyy-MM-dd") if self.use_date_checkbox.isChecked() else None

        self.image_list = self.db.get_filtered_images(
            only_untagged=only_untagged,
            people=selected_people or None,
            groups=selected_groups or None,
            emotions=selected_emotions or None,
            location=location,
            date=date
        )
        self.display_grid_view()
        self.show_toast("Filters applied.")

    def clear_filters(self):
        self.untagged_checkbox.setChecked(False)
        self.use_date_checkbox.setChecked(False)
        self.date_filter_input.setDate(QDate.currentDate())

        self.people_filter_list.clearSelection()
        self.group_filter_list.clearSelection()
        self.emotion_filter_list.clearSelection()

        self.scan_folder()
        self.show_toast("Filters cleared.")

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