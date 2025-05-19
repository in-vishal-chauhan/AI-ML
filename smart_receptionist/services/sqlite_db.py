import sqlite3
from logger import get_logger
import re
import subprocess

logger = get_logger(__name__)

class SqliteDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('ai.db')
        self.cursor = self.conn.cursor()

    def sanitize(self, val):
        if val:
            return re.sub(r'[^a-zA-Z0-9]', '', val.lower())
        return ''

    def generate_query(self, color, material, quality):
        query = "SELECT * FROM products WHERE 1=1"
        if color and color.strip() != "":
            query += " AND LOWER(REPLACE(REPLACE(REPLACE(color, ' ', ''), '-', ''), '_', '')) = ?"
        if material and material.strip() != "":
            query += " AND LOWER(REPLACE(REPLACE(REPLACE(material, ' ', ''), '-', ''), '_', '')) = ?"
        if quality and quality.strip() != "":
            query += " AND LOWER(REPLACE(REPLACE(REPLACE(quality, ' ', ''), '-', ''), '_', '')) = ?"
        return query

    def get_rate(self, color, material, quality):
        subprocess.run(['pyclean', '.'], check=True)
        try:
            sanitizeColor = self.sanitize(color)
            sanitizeMaterial = self.sanitize(material)
            sanitizeQuality = self.sanitize(quality)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    color TEXT DEFAULT NULL,
                    material TEXT DEFAULT NULL,
                    quality TEXT DEFAULT NULL,
                    rate REAL DEFAULT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_number TEXT DEFAULT NULL,
                    to_number TEXT DEFAULT NULL,
                    body TEXT,
                    full_payload TEXT DEFAULT NULL
                )
            """)

            query = self.generate_query(sanitizeColor, sanitizeMaterial, sanitizeQuality)
            params = []

            if color and color.strip() != "":
                params.append(sanitizeColor)
            if material and material.strip() != "":
                params.append(sanitizeMaterial)
            if quality and quality.strip() != "":
                params.append(sanitizeQuality)
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result if result else None
        except sqlite3.DatabaseError as e:
            logger.error(f"Sqlite error occurred while fetching rate: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return None

    def close(self):
        self.cursor.close()
        self.conn.close()
