import pymysql
from config import Config
from logger import get_logger
import re

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

    def get_rate(self, color, material, quality):
        try:
            query = """
                SELECT rate FROM products WHERE
                LOWER(REPLACE(REPLACE(REPLACE(color, ' ', ''), '-', ''), '_', '')) = %s
                AND LOWER(REPLACE(REPLACE(REPLACE(material, ' ', ''), '-', ''), '_', '')) = %s
                AND LOWER(REPLACE(REPLACE(REPLACE(quality, ' ', ''), '-', ''), '_', '')) = %s
            """
            self.cursor.execute(query, (
                self.sanitize(color),
                self.sanitize(material),
                self.sanitize(quality)
            ))
            result = self.cursor.fetchone()
            return result["rate"] if result else None
        except Exception as e:
            logger.error(f"DB get_rate() failed: {str(e)}")
            return None

    def close(self):
        self.cursor.close()
        self.conn.close()
