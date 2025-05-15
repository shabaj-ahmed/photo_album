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
        self.filter_panel.addWidget(QLabel("Filter by Location:"))
        self.location_filter_input = QLineEdit()
        self.filter_panel.addWidget(self.location_filter_input)

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
        self.location = QLineEdit()
        self.metadata_panel.addWidget(self.location)

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
            self.footer_widget.hide()
    
    def init_db(self):
        db_path = os.path.join(self.folder_path, "metadata.db")
        self.db = DatabaseManager(db_path)
    
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
        self.splitter.setSizes([0, 1, 0])

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
        self.splitter.setSizes([
            200 if self.filter_widget.isVisible() else 0,
            5,
            3
        ])
        self.prev_button.show()
        self.next_button.show()

        # Load from DB
        metadata = self.db.load_image_metadata(filename)
        people = set(self.db.get_people_for_image(filename))
        groups = set(self.db.get_groups_for_image(filename))
        emotions = set(self.db.get_emotions_for_image(filename))

        self.description.setPlainText(metadata["description"])
        self.location.setText(metadata["location"])
        if metadata["date"]:
            self.use_metadata_date_checkbox.setChecked(True)
            self.date.setEnabled(True)
            self.date.setDate(QDate.fromString(metadata["date"], "yyyy-MM-dd"))
        else:
            self.use_metadata_date_checkbox.setChecked(False)
            self.date.setEnabled(False)

        for i in range(self.people_list_widget.count()):
            item = self.people_list_widget.item(i)
            item.setSelected(item.text() in people)

        for i in range(self.group_list_widget.count()):
            item = self.group_list_widget.item(i)
            item.setSelected(item.text() in groups)

        for i in range(self.emotion_list_widget.count()):
            item = self.emotion_list_widget.item(i)
            item.setSelected(item.text() in emotions)

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
            location = self.location.text()
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
            self.filter_widget.show()
        self.update_splitter_sizes()

    def toggle_metadata_panel(self):
        if self.metadata_widget.isVisible():
            self.metadata_widget.hide()
        else:
            self.metadata_widget.show()
        self.update_splitter_sizes()

    def update_splitter_sizes(self):
        left = 200 if self.filter_widget.isVisible() else 0
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
        location = self.location_filter_input.text().strip()
        date = ""
        if self.date_filter_input.date() != self.date_filter_input.minimumDate():
            date = self.date_filter_input.date().toString("yyyy-MM-dd")

        self.image_list = self.db.get_filtered_images(
            only_untagged=only_untagged,
            people=selected_people,
            groups=selected_groups,
            emotions=selected_emotions,
            location=location,
            date=date
        )
        self.display_grid_view()

    def clear_filters(self):
        self.untagged_checkbox.setChecked(False)
        self.date_filter_input.setDate(self.date_filter_input.minimumDate())
        self.scan_folder()

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