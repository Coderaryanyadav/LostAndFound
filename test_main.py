"""
Unit Test Suite for main.py (Campus Desktop Application backend logic)
"""

import os
import sqlite3
import unittest
import main


class MainDesktopLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main.DB_FILE = "test_lost_found.db"
        if os.path.exists(main.DB_FILE):
            os.remove(main.DB_FILE)
        main.setup_database()

    @classmethod
    def tearDownClass(cls):
        try:
            if main.conn:
                main.conn.close()
        except Exception:
            pass
        if os.path.exists("test_lost_found.db"):
            os.remove("test_lost_found.db")

    def test_01_is_match(self):
        """Test matching logic flexibility"""
        # Exact match
        self.assertTrue(main.is_match("Water Bottle", "Blue", "Room 101", "Water Bottle", "Blue", "Room 101"))
        # Case insensitive & partial substring
        self.assertTrue(main.is_match("iphone 13", "Black", "Library", "Apple iPhone", "black", "Library 2nd floor"))
        # Different items
        self.assertFalse(main.is_match("Notebook", "Red", "Room 101", "Backpack", "Blue", "Room 101"))

    def test_02_database_tables_exist(self):
        """Verify all tables were created"""
        cursor = main.cursor
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        self.assertIn("students", tables)
        self.assertIn("lost_items", tables)
        self.assertIn("found_items", tables)
        self.assertIn("matches", tables)

    def test_03_student_insert_and_unique_constraint(self):
        """Verify student insertion and unique username constraint"""
        cursor = main.cursor
        cursor.execute(
            "INSERT INTO students(name, department, semester, username, password) VALUES (?, ?, ?, ?, ?)",
            ("Aryan Test", "Computer Science", 4, "aryan_test", "pass123")
        )
        main.conn.commit()

        # Duplicate should raise sqlite3.IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO students(name, department, semester, username, password) VALUES (?, ?, ?, ?, ?)",
                ("Duplicate", "IT", 2, "aryan_test", "pass456")
            )


if __name__ == '__main__':
    unittest.main()
