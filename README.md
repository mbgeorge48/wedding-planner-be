# Wedding Planner Backend

Backend for the Wedding Planner application, built with Django. This project manages wedding events, guests, food, venues, schedules, and RSVP functionality.

## Project Overview

This backend powers a wedding planning web app. It provides:

-   Event, guest, and RSVP management
-   Food and venue selection
-   Scheduling and timeline features
-   User authentication and admin controls
-   API endpoints for frontend integration

## Folder Structure

-   `project/` — Main Django project
    -   `data/` — Core app for models, migrations, and admin
        -   `models/` — Contains models for Person, Food, Venue, Wedding, Groups, etc.
        -   `migrations/` — Database migrations
        -   `admin.py` — Admin interface registration
    -   `interfaces/` — Handles routing and API/web interfaces
        -   `web/` — Web views, templates, static files
            -   `views/` — Web view logic (home, RSVP, schedule, time)
            -   `templates/` — HTML templates (base, index, RSVP, schedule)
            -   `static/` — Static assets (images, CSS, JS)
            -   `templatetags/` — Custom template filters

## Main Django Apps

-   **data**: Models and admin for all core entities (Person, Wedding, Food, Venue, Groups)
-   **interfaces**: URL routing, API endpoints, and web views

## Features

-   Manage weddings, guests, food, venues, and schedules
-   RSVP and group management
-   Custom template tags and filters
-   RESTful API endpoints
-   Admin dashboard

## Getting Started

### Prerequisites

-   Python 3.13.3
-   pip
-   virtualenv
-   PostgreSQL

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/mbgeorge48/wedding-planner-be.git
    cd wedding-planner-be
    ```
2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Configure environment variables:**
    - not setup yet
    - Copy `.env.example` to `.env` and update settings as needed (DB credentials, secret key, etc.)
5. **Apply migrations:**
    ```bash
    python manage.py migrate
    ```
6. **Create a superuser (optional):**
    ```bash
    python manage.py createsuperuser
    ```
7. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## API Endpoints

-   API routes are defined in `project/interfaces/api/`
-   Example: `/api/home/` for home page data

## Web Interface

-   Web views and templates in `project/interfaces/web/`
-   Main pages: Home, RSVP, Schedule

## Customization

-   Add new models in `project/data/models/`
-   Add new views in `project/interfaces/web/views/`
-   Add templates in `project/interfaces/web/templates/`

## Running Tests -- not setup yet

```bash
python manage.py test
```

## Contributing

Pull requests are welcome! Please follow PEP8 style and add docstrings. For major changes, open an issue first to discuss.

## License

MIT
