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
    
    def save_metadata(self, filename, description, people, groups, emotions, location, date):
        cursor = self.conn.cursor()

        # Step 1: Insert or update ImageMetadata
        cursor.execute("""
            INSERT INTO ImageMetadata (filename, description, location, date, tagged)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(filename) DO UPDATE SET
                description=excluded.description,
                location=excluded.location,
                date=excluded.date,
                tagged=1
        """, (filename, description, location, date))

        # Step 2: Get image ID
        cursor.execute("SELECT id FROM ImageMetadata WHERE filename = ?", (filename,))
        image_id = cursor.fetchone()[0]

        # Step 3: Clear old mappings
        cursor.execute("DELETE FROM ImagePerson WHERE image_id = ?", (image_id,))
        cursor.execute("DELETE FROM ImageGroup WHERE image_id = ?", (image_id,))
        cursor.execute("DELETE FROM ImageEmotion WHERE image_id = ?", (image_id,))

        # Step 4: Insert people
        for person_name in people:
            cursor.execute("INSERT OR IGNORE INTO Person (name) VALUES (?)", (person_name,))
            cursor.execute("SELECT id FROM Person WHERE name = ?", (person_name,))
            person_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO ImagePerson (image_id, person_id) VALUES (?, ?)", (image_id, person_id))

        # Step 5: Insert groups
        for group_name in groups:
            cursor.execute("INSERT OR IGNORE INTO GroupTag (name) VALUES (?)", (group_name,))
            cursor.execute("SELECT id FROM GroupTag WHERE name = ?", (group_name,))
            group_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO ImageGroup (image_id, group_id) VALUES (?, ?)", (image_id, group_id))

        # Step 6: Insert emotions
        for emotion_name in emotions:
            cursor.execute("INSERT OR IGNORE INTO EmotionTag (name) VALUES (?)", (emotion_name,))
            cursor.execute("SELECT id FROM EmotionTag WHERE name = ?", (emotion_name,))
            emotion_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO ImageEmotion (image_id, emotion_id) VALUES (?, ?)", (image_id, emotion_id))

        self.conn.commit()

    def load_image_metadata(self, filename):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT description, location, date
            FROM ImageMetadata
            WHERE filename = ?
        """, (filename,))
        row = cursor.fetchone()
        return {
            "description": row[0] if row else "",
            "location": row[1] if row else "",
            "date": row[2] if row else ""
        }
    
    def get_people_for_image(self, filename):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Person.name
            FROM ImagePerson
            JOIN Person ON ImagePerson.person_id = Person.id
            JOIN ImageMetadata ON ImagePerson.image_id = ImageMetadata.id
            WHERE ImageMetadata.filename = ?
        """, (filename,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_groups_for_image(self, filename):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT GroupTag.name
            FROM ImageGroup
            JOIN GroupTag ON ImageGroup.group_id = GroupTag.id
            JOIN ImageMetadata ON ImageGroup.image_id = ImageMetadata.id
            WHERE ImageMetadata.filename = ?
        """, (filename,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_emotions_for_image(self, filename):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT EmotionTag.name
            FROM ImageEmotion
            JOIN EmotionTag ON ImageEmotion.emotion_id = EmotionTag.id
            JOIN ImageMetadata ON ImageEmotion.image_id = ImageMetadata.id
            WHERE ImageMetadata.filename = ?
        """, (filename,))
        return [row[0] for row in cursor.fetchall()]

    def get_filtered_images(self, only_untagged=False, people=None, groups=None, emotions=None, location=None, date=None):
        cursor = self.conn.cursor()

        query = """
        SELECT DISTINCT im.filename
        FROM ImageMetadata im
        LEFT JOIN ImagePerson ip ON im.id = ip.image_id
        LEFT JOIN Person p ON ip.person_id = p.id
        LEFT JOIN ImageGroup ig ON im.id = ig.image_id
        LEFT JOIN GroupTag gt ON ig.group_id = gt.id
        LEFT JOIN ImageEmotion ie ON im.id = ie.image_id
        LEFT JOIN EmotionTag et ON ie.emotion_id = et.id
        WHERE 1 = 1
        """
        params = []

        if only_untagged:
            query += " AND im.tagged = 0"

        if people:
            placeholders = ",".join("?" for _ in people)
            query += f" AND p.name IN ({placeholders})"
            params.extend(people)

        if groups:
            placeholders = ",".join("?" for _ in groups)
            query += f" AND gt.name IN ({placeholders})"
            params.extend(groups)

        if emotions:
            placeholders = ",".join("?" for _ in emotions)
            query += f" AND et.name IN ({placeholders})"
            params.extend(emotions)

        if location:
            query += " AND im.location LIKE ?"
            params.append(f"%{location}%")

        if date:
            query += " AND im.date = ?"
            params.append(date)

        query += " ORDER BY im.date DESC"

        cursor.execute(query, params)
        return [row[0] for row in cursor.fetchall()]
