import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS ImageMetadata (
                id INTEGER PRIMARY KEY,
                filename TEXT UNIQUE,
                description TEXT,
                location TEXT,
                date TEXT,
                tagged INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS Person (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS ImagePerson (
                image_id INTEGER,
                person_id INTEGER,
                PRIMARY KEY (image_id, person_id),
                FOREIGN KEY (image_id) REFERENCES ImageMetadata(id),
                FOREIGN KEY (person_id) REFERENCES Person(id)
            );

            CREATE TABLE IF NOT EXISTS GroupTag (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS ImageGroup (
                image_id INTEGER,
                group_id INTEGER,
                PRIMARY KEY (image_id, group_id),
                FOREIGN KEY (image_id) REFERENCES ImageMetadata(id),
                FOREIGN KEY (group_id) REFERENCES GroupTag(id)
            );

            CREATE TABLE IF NOT EXISTS EmotionTag (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS ImageEmotion (
                image_id INTEGER,
                emotion_id INTEGER,
                PRIMARY KEY (image_id, emotion_id),
                FOREIGN KEY (image_id) REFERENCES ImageMetadata(id),
                FOREIGN KEY (emotion_id) REFERENCES EmotionTag(id)
            );
        """)
        self.conn.commit()

    def save_metadata(self, filename, description, people, groups, emotions, location, date):
        pass

    def insert_images_if_missing(self, filenames):
        """
        Add filenames to ImageMetadata if they don't already exist.
        Returns a list of filenames that are in the database (for UI display).
        """
        cursor = self.conn.cursor()
        for filename in filenames:
            cursor.execute("""
                INSERT OR IGNORE INTO ImageMetadata (filename)
                VALUES (?)
            """, (filename,))
        self.conn.commit()

        # Return all filenames known to the DB for display
        cursor.execute("SELECT filename FROM ImageMetadata")
        return [row[0] for row in cursor.fetchall()]
