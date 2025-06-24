from view.main_window import MainWindow
from model.database_manager import DatabaseManager
from PyQt6.QtWidgets import QFileDialog
import os


class MainController:
    def __init__(self):
        self.view = MainWindow()
        self.folder_path = None
        self.image_list = []
        self.people_list = []
        self.group_list = []
        self.emotion_list = []
        self.location_data = {
            'name': [],
            'category': [],
            'country': [],
            'region': [],
            'city': [],
            'postcode': []
        }

        # Connect UI callbacks to controller logic
        self.view.load_folder_callback = self.load_folder
        self.view.on_save_metadata = self.save_metadata
        self.view.on_apply_filters = self.apply_filters
        self.view.on_clear_filters = self.clear_filters
        self.view.fetch_metadata = self.get_metadata_for_image

        self.view.filter_panel.on_apply_filters = self.apply_filters
        self.view.filter_panel.on_clear_filters = self.clear_filters

    def run(self):
        self.view.show()

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self.view, "Select Image Folder")
        if not folder:
            return
        self.view.folder_path = folder
        self.view.load_button.hide()
        self.view.footer_widget.hide()
        self.view.filter_button.show()

        self.init_db(folder)
        self.scan_folder(folder)
        self.populate_people_list()
        self.populate_group_list()
        self.populate_emotion_list()
        self.populate_location_data()

    def init_db(self, folder):
        db_path = os.path.join(folder, "metadata.db")
        self.db = DatabaseManager(db_path)

    def scan_folder(self, folder):
        image_extensions = (".jpg", ".jpeg", ".png", ".raw",
                            ".heif", ".cr2", ".cr3", ".arw", ".tiff")
        files_in_folder = [
            f for f in os.listdir(folder) if f.lower().endswith(image_extensions)
        ]
        self.view.image_list = self.db.insert_images_if_missing(
            files_in_folder)
        self.view.display_grid_view()

    def populate_people_list(self):
        self.people_list = self.db.get_all_people_names()
        self.view.people_list = self.people_list
        self.view.populate_people_list(self.people_list)
        self.view.filter_panel.populate_people_filter_list()

    def populate_group_list(self):
        self.group_list = self.db.get_all_group_names()
        self.view.group_list = self.group_list
        self.view.populate_group_list(self.group_list)
        self.view.filter_panel.populate_group_filter_list()

    def populate_emotion_list(self):
        self.emotion_list = self.db.get_all_emotion_names()
        self.view.emotion_list = self.emotion_list
        self.view.populate_emotion_list(self.emotion_list)
        self.view.filter_panel.populate_emotion_filter_list()

    def populate_location_data(self):
        self.location_data = {
            'name': self.db.get_all_location_names(),
            'category': self.db.get_all_location_categories(),
            'country': self.db.get_all_location_countries(),
            'region': self.db.get_all_location_regions(),
            'city': self.db.get_all_location_cities(),
            'postcode': self.db.get_all_location_postcodes(),
        }

        # Update filters
        self.view.populate_location_list(
            self.view.filter_panel.location_name_filter_list, self.location_data['name'])
        self.view.populate_location_list(
            self.view.filter_panel.category_filter_list, self.location_data['category'])
        self.view.populate_location_list(
            self.view.filter_panel.region_filter_list, self.location_data['region'])
        self.view.populate_location_list(
            self.view.filter_panel.city_filter_list, self.location_data['city'])
        self.view.populate_location_list(
            self.view.filter_panel.country_filter_list, self.location_data['country'])

        # Update dropdowns
        self.view.name_dropdown.add_items(self.location_data['name'])
        self.view.category_dropdown.add_items(self.location_data['category'])
        self.view.country_dropdown.add_items(self.location_data['country'])
        self.view.region_dropdown.add_items(self.location_data['region'])
        self.view.city_dropdown.add_items(self.location_data['city'])
        self.view.postcode_dropdown.add_items(self.location_data['postcode'])

    def save_metadata(self, metadata):
        if not self.db:
            return

        self.db.save_metadata(
            filename=metadata['filename'],
            description=metadata['description'],
            people=metadata['people'],
            groups=metadata['groups'],
            emotions=metadata['emotions'],
            location=metadata['location'],
            date=metadata['date']
        )

        # Refresh location data to ensure filters and dropdowns are up to date
        self.populate_location_data()

        # self.view.toast("Metadata saved.")

    def apply_filters(self, filters):
        if not self.db:
            return

        filtered_images = self.db.get_filtered_images(
            only_untagged=filters.get("only_untagged", False),
            people=filters.get("people"),
            groups=filters.get("groups"),
            emotions=filters.get("emotions"),
            location=filters.get("location"),
            date=filters.get("date")
        )
        self.view.image_list = filtered_images
        self.view.display_grid_view()

    def clear_filters(self):
        if not self.db:
            return
        all_images = self.db.insert_images_if_missing(
            [f for f in os.listdir(self.view.folder_path) if f.lower().endswith(
                (".jpg", ".jpeg", ".png"))]
        )
        self.view.image_list = all_images
        self.view.display_grid_view()

    def get_metadata_for_image(self, filename):
        if not self.db:
            return None
        return self.db.load_image_metadata(filename)
