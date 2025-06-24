from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QListWidget, QListWidgetItem,
    QPushButton, QWidget, QDateEdit, QInputDialog
)
from PyQt6.QtCore import Qt, QDate
from .widgets.toast import Toast

# In filter_panel.py
class FilterPanel(QWidget):
    def __init__(self, people_list, group_list, emotion_list, on_apply_filters=None, on_clear_filters=None):
        super().__init__()
        self.people_list = people_list
        self.group_list = group_list
        self.emotion_list = emotion_list
        self.on_apply_filters = on_apply_filters
        self.on_clear_filters = on_clear_filters
        self.metadata_changed = False
        self.current_index = -1  # needed for collect_metadata, though may be redundant here

        self.setup_filter_panel()

    def setup_filter_panel(self):
        self.filter_panel = QVBoxLayout()

        # Tagged status
        self.filter_panel.addWidget(QLabel("Filter by Tagged Status:"))
        self.untagged_checkbox = QCheckBox("Show Only Untagged Images")
        self.filter_panel.addWidget(self.untagged_checkbox)

        # People
        self.filter_panel.addWidget(QLabel("Filter by People:"))
        self.people_filter_list = QListWidget()
        self.people_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.people_filter_list)
        self.populate_people_filter_list()

        # Group
        self.filter_panel.addWidget(QLabel("Filter by Group:"))
        self.group_filter_list = QListWidget()
        self.group_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.group_filter_list)
        self.populate_group_filter_list()

        # Emotion
        self.filter_panel.addWidget(QLabel("Filter by Emotion:"))
        self.emotion_filter_list = QListWidget()
        self.emotion_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.emotion_filter_list)
        self.populate_emotion_filter_list()

        # Location
        label = QLabel("Filter by location name:")
        self.location_name_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.location_name_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.location_name_filter_list)

        label = QLabel("Filter by Category:")
        self.category_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.category_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.category_filter_list)

        label = QLabel("Filter by Region:")
        self.region_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.region_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.region_filter_list)

        label = QLabel("Filter by City:")
        self.city_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.city_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.city_filter_list)

        label = QLabel("Filter by Country:")
        self.country_filter_list = QListWidget()
        self.filter_panel.addWidget(label)
        self.country_filter_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.filter_panel.addWidget(self.country_filter_list)

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
            lambda state: self.date_filter_input.setEnabled(
                state == Qt.CheckState.Checked.value)
        )

        # Filter controls
        self.reset_filter_button = QPushButton("Clear Filters")
        self.reset_filter_button.clicked.connect(
            lambda: self.on_clear_filters() if self.on_clear_filters else None
        )
        self.filter_panel.addWidget(self.reset_filter_button)

        self.apply_filter_button = QPushButton("Apply Filters")
        self.apply_filter_button.clicked.connect(
            lambda: self.on_apply_filters(
                self.collect_filter_data()) if self.on_apply_filters else None
        )

        self.filter_panel.addWidget(self.apply_filter_button)

        self.filter_widget = QWidget()
        self.filter_widget.setLayout(self.filter_panel)

    def populate_people_filter_list(self):
        self.people_filter_list.clear()
        for person in self.people_list:
            item = QListWidgetItem(person)
            self.people_filter_list.addItem(item)

    def populate_group_filter_list(self):
        self.group_filter_list.clear()
        for group in self.group_list:
            item = QListWidgetItem(group)
            self.group_filter_list.addItem(item)

    def populate_emotion_filter_list(self):
        self.emotion_filter_list.clear()
        for emotion in self.emotion_list:
            item = QListWidgetItem(emotion)
            self.emotion_filter_list.addItem(item)

    def collect_filter_data(self):
        only_untagged = self.untagged_checkbox.isChecked()

        people = [item.text()
                  for item in self.people_filter_list.selectedItems()]
        groups = [item.text()
                  for item in self.group_filter_list.selectedItems()]
        emotions = [item.text()
                    for item in self.emotion_filter_list.selectedItems()]

        location = {}
        if self.location_name_filter_list.selectedItems():
            location["name"] = [item.text()
                                for item in self.location_name_filter_list.selectedItems()]
        if self.category_filter_list.selectedItems():
            location["category"] = [item.text()
                                    for item in self.category_filter_list.selectedItems()]
        if self.region_filter_list.selectedItems():
            location["region"] = [item.text()
                                  for item in self.region_filter_list.selectedItems()]
        if self.city_filter_list.selectedItems():
            location["city"] = [item.text()
                                for item in self.city_filter_list.selectedItems()]
        if self.country_filter_list.selectedItems():
            location["country"] = [item.text()
                                   for item in self.country_filter_list.selectedItems()]

        # Only include location if at least one field is selected
        location = location if location else None

        date = self.date_filter_input.date().toString(
            "yyyy-MM-dd") if self.use_date_checkbox.isChecked() else None

        Toast(self, "Filters applied.")

        return {
            "only_untagged": only_untagged,
            "people": people or None,
            "groups": groups or None,
            "emotions": emotions or None,
            "location": location,
            "date": date
        }

    def clear_filters(self):
        self.untagged_checkbox.setChecked(False)

        self.people_filter_list.clearSelection()
        self.group_filter_list.clearSelection()
        self.emotion_filter_list.clearSelection()
        self.location_name_filter_list.clearSelection()
        self.category_filter_list.clearSelection()
        self.region_filter_list.clearSelection()
        self.city_filter_list.clearSelection()
        self.country_filter_list.clearSelection()

        self.use_date_checkbox.setChecked(False)
        self.date_filter_input.setDate(QDate.currentDate())

        Toast(self, "Filters cleared.")
