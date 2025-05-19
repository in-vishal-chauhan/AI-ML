from services.sqlite_db import SqliteDatabase

class ProductSeeder:
    def __init__(self):
        self.db = SqliteDatabase()

    def seed(self):
        products = [
            ("Red", "Cotton", "Super Deluxe", 120.00),
            ("Red", "Cotton", "Deluxe", 100.00),
            ("Red", "Cotton", "Prime", 80.00),
            ("Yellow", "TerryCotton", "Super Deluxe", 140.00),
            ("Pink", "cotton", "high", 600.00),
            ("white", "silk", "low", 786.00),
            ("pink", "silk", "nice", 420.00),
            ("green", "silk", "high", 123.00),
            ("orange", "silk", "high", 222.00),
            ("green", "cotton", "best", 310.00),
        ]

        try:
            self.db.cursor.executemany("""
                INSERT INTO products (color, material, quality, rate)
                VALUES (?, ?, ?, ?)
            """, products)
            self.db.conn.commit()
            print("Products seeded successfully.")
        except Exception as e:
            print(f"Error seeding database: {e}")
        finally:
            self.db.close()

if __name__ == "__main__":
    seeder = ProductSeeder()
    seeder.seed()
