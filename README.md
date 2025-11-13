# Campus Connect - Backend

## 1. Project Overview

Campus Connect is a real-world event management backend built with **Django + Django REST Framework (DRF)**. It supports two user roles — **Student**, and **Admin**, — and provides features for creating events, registering/unregistering students, seat management, venue selection, and role-based access.

This repository contains the backend APIs and core business logic for the company project `campus-connect-backend`.

---

## 2. Key Features

1. Role-based authentication and authorization (Student, Admin).
2. Students can sign up, login, view events (upcoming + past) and register/unregister for events.
3. Super Admin creates Admin accounts .
4. Admins can create, view, and delete events. Deleting an event removes related registrations.
5. Venue and schedule conflict validation: Admin cannot create two events at the same location at the same date/time.
6. Seat management: Admin specifies total seats for an event. Available seats decrease as students register.
7. Event registration is blocked if the event date-time is in the past or if no seats remain.

---

## 3. Tech Stack

- Python (3.10/3.11/3.12)
- Django 4.x
- Django REST Framework
- PostgreSQL


---

## 4. Important Business Rules / Validations

1. **Admin creation**: Only Super Admin can create Admin users.
2. **Student signup**: Students self-register. After signup, redirect them to login.
3. **Event visibility**: After login, students see all events and the events they are already registered for on the same page. Each event must display available seats.
4. **Registration constraints**:
   - Students cannot register for events whose `start_time` is earlier than the current time (past events).
   - Students can unregister from an event; unregistering increments event available seats.
5. **Event creation constraints** (Admin)
   - Validate there is no other event at the **same location** whose time overlaps.
   - Admin must provide `seats` (total capacity) and optionally `location.capacity` is used to cap `seats`.
   - When registrations increase, `available_seats = seats - registered_count` decreases automatically.
6. **Event deletion**: Deleting an event by Admin deletes related registrations (or marks them deleted) so students’ registration lists are updated.

---

## 5. Quick Start — Local Setup


1. Clone the repo

```bash
git clone <repo-url>
cd campus-connect-backend
```

2. Create and activate virtual env

```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
# venv\Scripts\activate   # Windows
```

3. Upgrade pip and install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create `.env` (or modify `settings.py` to read env). Example variables:

```ini
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

5. Run migrations

```bash
python manage.py migrate
```

6. Create Superuser (super admin)

```bash
python manage.py createsuperuser
# You can also seed a Super Admin using a custom management command or fixtures
```

7. Run the server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000` to try the APIs.

---

## 6. Useful Management Commands / Helpers

- Create a super admin via Django `createsuperuser` or a custom management command that assigns the Super Admin role in `Users_Roles`.
- Create admin user workflow:
  - Super Admin calls `POST /api/admins/` with `email` and `name`.
  - System creates a user with Admin role
---
## 7. Folder structure

```bas
   campus-connect-backend
   ├── __pycache__
   │   └── tests_user_creation.cpython-313-pytest-9.0.1.pyc
   ├── campus_connect
   │   ├── __init__.py
   │   ├── __pycache__
   │   ├── asgi.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── manage.py
   ├── pytest.ini
   ├── README.md
   ├── requirements.txt
   ├── tests
   │   ├── __pycache__
   │   └── test_user_creation.py
   └── venv
      ├── bin
      ├── include
      ├── lib
      └── pyvenv.cfg




