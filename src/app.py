"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

current_dir = Path(__file__).parent
DATABASE_PATH = Path(
    os.environ.get("ACTIVITY_DATABASE_PATH", str(current_dir / "activities.db"))
)

DEFAULT_CLUBS = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "category": "Academic",
        "contact_info": "chess@mergington.edu",
    },
    {
        "name": "STEM Club",
        "description": "Explore programming, mathematics, and technology",
        "category": "Academic",
        "contact_info": "stem@mergington.edu",
    },
    {
        "name": "Athletics Club",
        "description": "Take part in school sports and physical activities",
        "category": "Sports",
        "contact_info": "athletics@mergington.edu",
    },
    {
        "name": "Arts Club",
        "description": "Create art, perform, and produce school plays",
        "category": "Arts",
        "contact_info": "arts@mergington.edu",
    },
    {
        "name": "Debate Club",
        "description": "Develop public speaking and argumentation skills",
        "category": "Academic",
        "contact_info": "debate@mergington.edu",
    },
]

DEFAULT_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "club": "Chess Club",
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "club": "STEM Club",
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "club": "Athletics Club",
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "club": "Athletics Club",
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "club": "Athletics Club",
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "club": "Arts Club",
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "club": "Arts Club",
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "club": "STEM Club",
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "club": "Debate Club",
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@contextmanager
def database_connection() -> Iterator[sqlite3.Connection]:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with database_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS clubs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                contact_info TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activities (
                name TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                schedule TEXT NOT NULL,
                max_participants INTEGER NOT NULL,
                club_id INTEGER NOT NULL REFERENCES clubs(id)
            );
            CREATE TABLE IF NOT EXISTS memberships (
                club_id INTEGER NOT NULL REFERENCES clubs(id),
                email TEXT NOT NULL,
                PRIMARY KEY (club_id, email)
            );
            CREATE TABLE IF NOT EXISTS registrations (
                activity_name TEXT NOT NULL REFERENCES activities(name),
                email TEXT NOT NULL,
                PRIMARY KEY (activity_name, email)
            );
            """
        )

        for club in DEFAULT_CLUBS:
            connection.execute(
                """
                INSERT OR IGNORE INTO clubs (name, description, category, contact_info)
                VALUES (?, ?, ?, ?)
                """,
                (club["name"], club["description"], club["category"], club["contact_info"]),
            )

        club_ids = {
            row["name"]: row["id"]
            for row in connection.execute("SELECT id, name FROM clubs")
        }
        for name, activity in DEFAULT_ACTIVITIES.items():
            club_id = club_ids[activity["club"]]
            connection.execute(
                """
                INSERT OR IGNORE INTO activities
                    (name, description, schedule, max_participants, club_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    activity["description"],
                    activity["schedule"],
                    activity["max_participants"],
                    club_id,
                ),
            )
            for email in activity["participants"]:
                connection.execute(
                    "INSERT OR IGNORE INTO memberships (club_id, email) VALUES (?, ?)",
                    (club_id, email),
                )
                connection.execute(
                    "INSERT OR IGNORE INTO registrations (activity_name, email) VALUES (?, ?)",
                    (name, email),
                )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(email: str | None = None):
    with database_connection() as connection:
        rows = connection.execute(
            """
            SELECT a.name, a.description, a.schedule, a.max_participants,
                   c.name AS club_name,
                   EXISTS (
                       SELECT 1 FROM memberships m
                       WHERE m.club_id = a.club_id AND m.email = ?
                   ) AS is_member
            FROM activities a
            JOIN clubs c ON c.id = a.club_id
            ORDER BY a.name
            """,
            (email or "",),
        ).fetchall()
        return {
            row["name"]: {
                "description": row["description"],
                "schedule": row["schedule"],
                "max_participants": row["max_participants"],
                "participants": [
                    participant["email"]
                    for participant in connection.execute(
                        "SELECT email FROM registrations WHERE activity_name = ? ORDER BY email",
                        (row["name"],),
                    )
                ],
                "club_name": row["club_name"],
                "is_member": bool(row["is_member"]),
            }
            for row in rows
        }


@app.get("/clubs")
def get_clubs(email: str | None = None):
    with database_connection() as connection:
        rows = connection.execute(
            """
            SELECT c.name, c.description, c.category, c.contact_info,
                   EXISTS (
                       SELECT 1 FROM memberships m
                       WHERE m.club_id = c.id AND m.email = ?
                   ) AS is_member
            FROM clubs c
            ORDER BY c.name
            """,
            (email or "",),
        ).fetchall()
        return [
            {
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "contact_info": row["contact_info"],
                "is_member": bool(row["is_member"]),
            }
            for row in rows
        ]


@app.post("/clubs/{club_name}/join")
def join_club(club_name: str, email: str):
    with database_connection() as connection:
        club = connection.execute(
            "SELECT id FROM clubs WHERE name = ?", (club_name,)
        ).fetchone()
        if club is None:
            raise HTTPException(status_code=404, detail="Club not found")

        try:
            connection.execute(
                "INSERT INTO memberships (club_id, email) VALUES (?, ?)",
                (club["id"], email),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Student is already a member of this club",
            ) from None
    return {"message": f"Joined {club_name}"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    with database_connection() as connection:
        activity = connection.execute(
            """
            SELECT a.club_id, a.max_participants, c.name AS club_name
            FROM activities a JOIN clubs c ON c.id = a.club_id
            WHERE a.name = ?
            """,
            (activity_name,),
        ).fetchone()
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")

        membership = connection.execute(
            "SELECT 1 FROM memberships WHERE club_id = ? AND email = ?",
            (activity["club_id"], email),
        ).fetchone()
        if membership is None:
            raise HTTPException(
                status_code=403,
                detail=f"Join {activity['club_name']} before registering for this activity",
            )

        registered = connection.execute(
            "SELECT 1 FROM registrations WHERE activity_name = ? AND email = ?",
            (activity_name, email),
        ).fetchone()
        if registered is not None:
            raise HTTPException(
                status_code=400,
                detail="Student is already signed up"
            )

        count = connection.execute(
            "SELECT COUNT(*) AS total FROM registrations WHERE activity_name = ?",
            (activity_name,),
        ).fetchone()["total"]
        if count >= activity["max_participants"]:
            raise HTTPException(status_code=400, detail="Activity is full")

        connection.execute(
            "INSERT INTO registrations (activity_name, email) VALUES (?, ?)",
            (activity_name, email),
        )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    with database_connection() as connection:
        activity = connection.execute(
            "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
        ).fetchone()
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")

        registration = connection.execute(
            "SELECT 1 FROM registrations WHERE activity_name = ? AND email = ?",
            (activity_name, email),
        ).fetchone()
        if registration is None:
            raise HTTPException(
                status_code=400,
                detail="Student is not signed up for this activity"
            )

        connection.execute(
            "DELETE FROM registrations WHERE activity_name = ? AND email = ?",
            (activity_name, email),
        )
    return {"message": f"Unregistered {email} from {activity_name}"}
