import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from src import app as app_module


class ClubMembershipTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.database_path_patch = patch.object(
            app_module, "DATABASE_PATH", self.database_path
        )
        self.database_path_patch.start()
        app_module.initialize_database()

    def tearDown(self):
        self.database_path_patch.stop()
        self.temp_dir.cleanup()

    def test_clubs_can_be_joined_only_once(self):
        clubs = app_module.get_clubs(email="student@mergington.edu")
        stem_club = next(club for club in clubs if club["name"] == "STEM Club")
        self.assertFalse(stem_club["is_member"])

        app_module.join_club("STEM Club", "student@mergington.edu")
        clubs = app_module.get_clubs(email="student@mergington.edu")
        stem_club = next(club for club in clubs if club["name"] == "STEM Club")
        self.assertTrue(stem_club["is_member"])

        with self.assertRaises(HTTPException) as error:
            app_module.join_club("STEM Club", "student@mergington.edu")
        self.assertEqual(error.exception.status_code, 400)

    def test_registration_requires_membership_and_persists(self):
        with self.assertRaises(HTTPException) as error:
            app_module.signup_for_activity(
                "Programming Class", "student@mergington.edu"
            )
        self.assertEqual(error.exception.status_code, 403)

        app_module.join_club("STEM Club", "student@mergington.edu")
        app_module.signup_for_activity("Programming Class", "student@mergington.edu")
        app_module.initialize_database()

        activity = app_module.get_activities("student@mergington.edu")[
            "Programming Class"
        ]
        self.assertTrue(activity["is_member"])
        self.assertIn("student@mergington.edu", activity["participants"])

    def test_duplicate_registration_and_capacity_are_rejected(self):
        with self.assertRaises(HTTPException) as duplicate_error:
            app_module.signup_for_activity("Chess Club", "michael@mergington.edu")
        self.assertEqual(duplicate_error.exception.status_code, 400)

        app_module.join_club("Chess Club", "student@mergington.edu")
        with app_module.database_connection() as connection:
            connection.execute(
                "UPDATE activities SET max_participants = 2 WHERE name = 'Chess Club'"
            )

        with self.assertRaises(HTTPException) as capacity_error:
            app_module.signup_for_activity("Chess Club", "student@mergington.edu")
        self.assertEqual(capacity_error.exception.status_code, 400)
        self.assertEqual(capacity_error.exception.detail, "Activity is full")


if __name__ == "__main__":
    unittest.main()