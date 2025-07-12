from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QCheckBox, QTextEdit,
    QListWidget, QDateEdit, QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import Qt, QDate
from .widgets.editable_dropdown import EditableDropdown
from .widgets.toast import Toast

class MetadataPanel(QWidget):
    def __init__(self, db, people_list, group_list, emotion_list, on_save_metadata=None):
        super().__init__()
        self.db = db
        self.people_list_data = people_list
        self.group_list_data = group_list
        self.emotion_list_data = emotion_list
        self.on_save_metadata = on_save_metadata
        self.metadata_changed = False
        self.current_index = -1
        self.image_list = []
        self.current_filename = None

        self.setup_metadata_panel()

    def setup_metadata_panel(self):
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Description:"))
        self.description = QTextEdit()
        self.layout.addWidget(self.description)

        self.layout.addWidget(QLabel("Who is in the photo:"))
        self.people_list_widget = QListWidget()
        self.people_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.people_list_widget.itemClicked.connect(self.handle_person_click)
        self.layout.addWidget(self.people_list_widget)
        self.populate_people_list(self.people_list_data)

        self.layout.addWidget(QLabel("Group:"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.group_list_widget.itemClicked.connect(self.handle_group_click)
        self.layout.addWidget(self.group_list_widget)
        self.populate_group_list(self.group_list_data)

        self.layout.addWidget(QLabel("Emotion:"))
        self.emotion_list_widget = QListWidget()
        self.emotion_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.emotion_list_widget.itemClicked.connect(self.handle_emotion_click)
        self.layout.addWidget(self.emotion_list_widget)
        self.populate_emotion_list(self.emotion_list_data)

        self.layout.addWidget(QLabel("Location:"))
        self.use_location_checkbox = QCheckBox("Specify Location")
        self.layout.addWidget(self.use_location_checkbox)

        self.name_dropdown = EditableDropdown(
            label="name",
            values=[],
            parent=self,
            remove_callback=lambda val: self.db.delete_location_entry("name", val)
        )
        self.category_dropdown = EditableDropdown(
            label="category",
            values=[],
            parent=self,
            remove_callback=lambda val: self.db.delete_location_entry("category", val)
        )
        self.country_dropdown = EditableDropdown(
            label="country",
            values=[],
            parent=self,
            remove_callback=lambda val: self.db.delete_location_entry("country", val)
        )
        self.region_dropdown = EditableDropdown(
            label="region",
            values=[],
            parent=self,
            remove_callback=lambda val: self.db.delete_location_entry("region", val)
        )
        self.city_dropdown = EditableDropdown(
            label="city",
            values=[],
            parent=self,
            remove_callback=lambda val: self.db.delete_location_entry("city", val)
        )
        self.postcode_dropdown = EditableDropdown(
            label="postcode",
            values=[],
            parent=self,
            remove_callback=lambda val: self.db.delete_location_entry("postcode", val)
        )

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
        self.location_container.setVisible(False)
        self.layout.addWidget(self.location_container)

        self.layout.addWidget(QLabel("Date:"))
        self.use_metadata_date_checkbox = QCheckBox("Specify Date")
        self.layout.addWidget(self.use_metadata_date_checkbox)
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate.currentDate())
        self.date.setEnabled(False)
        self.use_metadata_date_checkbox.stateChanged.connect(
            lambda state: self.date.setEnabled(state == Qt.CheckState.Checked.value)
        )
        self.layout.addWidget(self.date)

        self.save_button = QPushButton("Save Metadata")
        self.save_button.clicked.connect(lambda: self.on_save_metadata(self.collect_metadata()) if self.on_save_metadata else None)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def populate_people_list(self, people):
        self.people_list_widget.clear()
        for person in people:
            self.people_list_widget.addItem(QListWidgetItem(person))
        self.people_list_widget.addItem(QListWidgetItem("+ Add New..."))

    def handle_person_click(self, item):
        if item.text() == "+ Add New...":
            name, ok = QInputDialog.getText(self, "Add Person", "Enter person's name:")
            if ok and name.strip():
                name = name.strip()
                current_people = [self.people_list_widget.item(i).text() for i in range(self.people_list_widget.count() - 1)]
                if name not in current_people:
                    current_people.append(name)
                    self.populate_people_list(current_people)
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
            name, ok = QInputDialog.getText(self, "Add Group", "Enter group name:")
            if ok and name.strip():
                name = name.strip()
                current_groups = [self.group_list_widget.item(i).text() for i in range(self.group_list_widget.count() - 1)]
                if name not in current_groups:
                    current_groups.append(name)
                    self.populate_group_list(current_groups)
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
            name, ok = QInputDialog.getText(self, "Add Emotion", "Enter emotion:")
            if ok and name.strip():
                name = name.strip()
                current_emotions = [self.emotion_list_widget.item(i).text() for i in range(self.emotion_list_widget.count() - 1)]
                if name not in current_emotions:
                    current_emotions.append(name)
                    self.populate_emotion_list(current_emotions)
                    for i in range(self.emotion_list_widget.count()):
                        if self.emotion_list_widget.item(i).text() == name:
                            self.emotion_list_widget.item(i).setSelected(True)
                            break
                    self.metadata_changed = True

    def collect_metadata(self):
        description = self.description.toPlainText()
        date = self.date.date().toString("yyyy-MM-dd") if self.use_metadata_date_checkbox.isChecked() else ""

        selected_people = [item.text() for item in self.people_list_widget.selectedItems() if item.text() != "+ Add New..."]
        selected_groups = [item.text() for item in self.group_list_widget.selectedItems() if item.text() != "+ Add New..."]
        selected_emotions = [item.text() for item in self.emotion_list_widget.selectedItems() if item.text() != "+ Add New..."]

        if self.use_location_checkbox.isChecked():
            location = {
                "name": self.name_dropdown.get_selected_value(),
                "category": self.category_dropdown.get_selected_value(),
                "country": self.country_dropdown.get_selected_value(),
                "region": self.region_dropdown.get_selected_value(),
                "city": self.city_dropdown.get_selected_value(),
                "postcode": self.postcode_dropdown.get_selected_value()
            }
        else:
            location = None

        Toast(self, "Metadata saved.")

        return {
            "filename": self.current_filename,
            "description": description,
            "people": selected_people,
            "groups": selected_groups,
            "emotions": selected_emotions,
            "location": location,
            "date": date
        }

    def set_current_filename(self, filename):
        self.current_filename = filename
