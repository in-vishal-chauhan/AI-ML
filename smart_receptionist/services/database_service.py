import pymysql
from config import Config
from logger import get_logger
import re
import subprocess

logger = get_logger(__name__)

class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.conn.cursor()

    def sanitize(self, val):
        return re.sub(r'[^a-zA-Z0-9]', '', val.lower())

    def generate_query(self, color, material, quality):
        query = "SELECT * FROM products WHERE 1=1"
        if color and color.strip() != "":
            query += " AND LOWER(REPLACE(REPLACE(REPLACE(color, ' ', ''), '-', ''), '_', '')) = %s"
        if material and material.strip() != "":
            query += " AND LOWER(REPLACE(REPLACE(REPLACE(material, ' ', ''), '-', ''), '_', '')) = %s"
        if quality and quality.strip() != "":
            query += " AND LOWER(REPLACE(REPLACE(REPLACE(quality, ' ', ''), '-', ''), '_', '')) = %s"
        return query

    def get_rate(self, color, material, quality):
        subprocess.run(['pyclean', '.'], check=True)
        try:
            sanitizeColor = self.sanitize(color)
            sanitizeMaterial = self.sanitize(material)
            sanitizeQuality = self.sanitize(quality)
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
        except pymysql.MySQLError as e:
            logger.error(f"MySQL error occurred while fetching rate: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return None

    def close(self):
        self.cursor.close()
        self.conn.close()
