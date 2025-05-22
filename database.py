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
                date TEXT,
                tagged INTEGER DEFAULT 0,
                location_id INTEGER,
                FOREIGN KEY (location_id) REFERENCES Location(id)
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
            
            CREATE TABLE IF NOT EXISTS Location (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                postcode TEXT
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
        location_id = self.get_or_create_location(location) if location else None

        cursor.execute("""
            INSERT INTO ImageMetadata (filename, description, location_id, date, tagged)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(filename) DO UPDATE SET
                description=excluded.description,
                location_id=excluded.location_id,
                date=excluded.date,
                tagged=1
        """, (filename, description, location_id, date))


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

        # Step 7: Insert location
        location_id = self.get_or_create_location(location) if location else None

        self.conn.commit()
    
    def get_or_create_location(self, location_data):
        """
        Accepts a dictionary with fields: name, category, country, region, city, postcode.
        Returns the ID of the location.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM Location
            WHERE name = ? AND category IS ? AND country IS ? AND region IS ? AND city IS ? AND postcode IS ?
        """, (
            location_data.get("name"),
            location_data.get("category"),
            location_data.get("country"),
            location_data.get("region"),
            location_data.get("city"),
            location_data.get("postcode")
        ))
        result = cursor.fetchone()
        if result:
            return result[0]

        cursor.execute("""
            INSERT INTO Location (name, category, country, region, city, postcode)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            location_data.get("name"),
            location_data.get("category"),
            location_data.get("country"),
            location_data.get("region"),
            location_data.get("city"),
            location_data.get("postcode")
        ))
        self.conn.commit()
        return cursor.lastrowid

    def load_image_metadata(self, filename):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT im.description, im.date,
                l.name, l.category, l.country, l.region, l.city, l.postcode
            FROM ImageMetadata im
            LEFT JOIN Location l ON im.location_id = l.id
            WHERE im.filename = ?
        """, (filename,))
        row = cursor.fetchone()
        return {
            "description": row[0] if row else "",
            "date": row[1] if row else "",
            "location": {
                "name": row[2],
                "category": row[3],
                "country": row[4],
                "region": row[5],
                "city": row[6],
                "postcode": row[7],
            } if row and row[2] else None,
            "people": self.get_people_for_image(filename),
            "groups": self.get_groups_for_image(filename),
            "emotions": self.get_emotions_for_image(filename)
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
        LEFT JOIN Location l ON im.location_id = l.id
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
            if location.get("name"):
                query += " AND l.name = ?"
                params.append(location["name"])
            if location.get("category"):
                query += " AND l.category = ?"
                params.append(location["category"])
            if location.get("country"):
                query += " AND l.country = ?"
                params.append(location["country"])
            if location.get("region"):
                query += " AND l.region = ?"
                params.append(location["region"])
            if location.get("city"):
                query += " AND l.city = ?"
                params.append(location["city"])

        if date:
            query += " AND im.date = ?"
            params.append(date)

        query += " ORDER BY im.date DESC"

        cursor.execute(query, params)
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_location_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM Location WHERE name IS NOT NULL")
        print(f"############## All location names: {cursor.fetchall()}")
        return [row[0] for row in cursor.fetchall()]

    def get_all_location_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM Location WHERE category IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_location_countries(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT country FROM Location WHERE country IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_location_regions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT region FROM Location WHERE region IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_location_cities(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT city FROM Location WHERE city IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_location_postcodes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT postcode FROM Location WHERE postcode IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]
    
    def delete_location_entry(self, field_name, value):
        if field_name not in ["name", "category", "country", "region", "city", "postcode"]:
            raise ValueError(f"Invalid location field: {field_name}")
        cursor = self.conn.cursor()
        cursor.execute(f"""
            DELETE FROM Location
            WHERE {field_name} = ? AND
                NOT EXISTS (
                    SELECT 1 FROM ImageMetadata
                    WHERE Location.id = ImageMetadata.location_id
                )
        """, (value,))
        self.conn.commit()
