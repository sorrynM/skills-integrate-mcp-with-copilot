# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Browse clubs and join them
- Register for activities hosted by clubs you have joined
- Persist club memberships and activity registrations in SQLite

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/clubs?email=student@mergington.edu`                             | List clubs and show membership state for the supplied email         |
| POST   | `/clubs/{club_name}/join?email=student@mergington.edu`            | Join a club                                                         |
| GET    | `/activities?email=student@mergington.edu`                        | List activities, host clubs, and membership state                   |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Register for an activity after joining its host club                |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                      |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Clubs, memberships, and registrations are stored in `src/activities.db` and remain available after the server restarts. Set `ACTIVITY_DATABASE_PATH` to use a different SQLite file.
