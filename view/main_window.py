import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QScrollArea, QGridLayout, QSplitter,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate

from .widgets.editable_dropdown import EditableDropdown
from .filter_panel import FilterPanel
from .metadata_panel import MetadataPanel

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

        self.setup_ui()

    def setup_ui(self):
        self.root_layout = QVBoxLayout()
        self.setLayout(self.root_layout)

        self.setup_header()
        self.filter_panel = FilterPanel(
            self.people_list,
            self.group_list,
            self.emotion_list,
        )
        self.metadata_panel = MetadataPanel(
            self.db,
            self.people_list,
            self.group_list,
            self.emotion_list,
        )
        self.setup_image_panels()
        self.setup_splitter()
        self.setup_footer()

        # Initial splitter state
        self.filter_panel.hide()
        self.metadata_panel.hide()
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
        self.splitter.addWidget(self.filter_panel)
        self.splitter.addWidget(self.main_view_widget)
        self.splitter.addWidget(self.metadata_panel)
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
        self.metadata_panel.hide()
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
        self.metadata_panel.set_current_filename(filename)
        image_path = os.path.join(self.folder_path, filename)
        pixmap = QPixmap(image_path).scaledToWidth(
            800, Qt.TransformationMode.SmoothTransformation)
        self.full_image_label.setPixmap(pixmap)
        self.scroll_area.hide()
        self.splitter.show()
        self.full_image_label.show()
        self.metadata_panel.show()
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

        self.metadata_panel.description.setPlainText(metadata["description"])
        if metadata["date"]:
            self.metadata_panel.use_metadata_date_checkbox.setChecked(True)
            self.metadata_panel.date.setEnabled(True)
            self.metadata_panel.date.setDate(QDate.fromString(metadata["date"], "yyyy-MM-dd"))
        else:
            self.metadata_panel.use_metadata_date_checkbox.setChecked(False)
            self.metadata_panel.date.setEnabled(False)

        for i in range(self.metadata_panel.people_list_widget.count()):
            item = self.metadata_panel.people_list_widget.item(i)
            item.setSelected(item.text() in metadata["people"])

        for i in range(self.metadata_panel.group_list_widget.count()):
            item = self.metadata_panel.group_list_widget.item(i)
            item.setSelected(item.text() in metadata["groups"])

        for i in range(self.metadata_panel.emotion_list_widget.count()):
            item = self.metadata_panel.emotion_list_widget.item(i)
            item.setSelected(item.text() in metadata["emotions"])

        # Populate location fields if location is present
        location = metadata.get("location")
        if location:
            self.metadata_panel.use_location_checkbox.setChecked(True)
            self.metadata_panel.location_container.setVisible(True)

            self.metadata_panel.name_dropdown.setCurrentText(location.get("name") or "")
            self.metadata_panel.category_dropdown.setCurrentText(
                location.get("category") or "")
            self.metadata_panel.country_dropdown.setCurrentText(location.get("country") or "")
            self.metadata_panel.region_dropdown.setCurrentText(location.get("region") or "")
            self.metadata_panel.city_dropdown.setCurrentText(location.get("city") or "")
            self.metadata_panel.postcode_dropdown.setCurrentText(
                location.get("postcode") or "")
        else:
            self.metadata_panel.use_location_checkbox.setChecked(False)
            self.metadata_panel.location_container.setVisible(False)

            self.metadata_panel.name_dropdown.setCurrentIndex(-1)
            self.metadata_panel.category_dropdown.setCurrentIndex(-1)
            self.metadata_panel.country_dropdown.setCurrentIndex(-1)
            self.metadata_panel.region_dropdown.setCurrentIndex(-1)
            self.metadata_panel.city_dropdown.setCurrentIndex(-1)
            self.metadata_panel.postcode_dropdown.setCurrentIndex(-1)

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
        if self.filter_panel.isVisible():
            self.filter_panel.hide()
        else:
            self.filter_panel.show()
        self.update_splitter_sizes()

    def toggle_metadata_panel(self):
        if self.metadata_panel.isVisible():
            self.metadata_panel.hide()
        else:
            self.metadata_panel.show()
        self.update_splitter_sizes()

    def update_splitter_sizes(self):
        left = 300 if self.filter_panel.isVisible() else 0
        right = 300 if self.metadata_panel.isVisible() else 0
        center = max(600, self.width() - left - right)
        self.splitter.setSizes([left, center, right])

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()