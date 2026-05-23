# Wedding Planner RSVP System

A professional, containerized Django application for managing wedding RSVPs, guest lists, and event details.

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.13+
- Docker & Docker Compose (Optional, but recommended)
- PostgreSQL (if running without Docker)

### Option 1: Using Docker (Easiest)

Run the entire stack (Django + Postgres) with a single command:

```bash
docker-compose up
```

The app will be available at `http://localhost:8000`.

### Option 2: Manual Setup

1. **Environment**: Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```
2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Database**: Ensure PostgreSQL is running and matches your `.env` settings.
4. **Run**:
    ```bash
    python manage.py migrate
    scripts/server
    ```

---

## 🛠 Project Scripts (`/scripts`)

The `scripts/` directory contains helper utilities for common tasks:

- **`entrypoint.sh`**: **(Production Only)** Automatically runs migrations, collects static files, and starts the Gunicorn server. Used by Docker.
- **`server`**: Starts the local Django development server.
- **`setup`**: Initial environment setup script.
- **`test`**: Runs the project test suite.
- **`format`**: Runs code formatters (Black/Isort) to keep the codebase clean.
- **`console`**: Opens a Django shell for direct database/model interaction.

---

## 📋 Management Commands

Custom Django commands are located in `project/data/management/commands/`:

### `initialise_wedding`

Used to set up a new wedding instance. It will prompt you for bride/groom details, venue information, and the wedding date/time.

```bash
python manage.py initialise_wedding
```

### `import_csv_guest_list`

Bulk imports guests from a CSV file. Use the `--force` flag to update existing guests.

```bash
python manage.py import_csv_guest_list path/to/guests.csv --force
```

### `generate_guest_urls`

Generates unique RSVP links for every guest. Can also generate QR code images for physical invitations.

```bash
python manage.py generate_guest_urls --base-url https://yourwedding.com --create-qr-codes
```

---

## 🌐 Production & Deployment

This project is configured for easy deployment to **Railway.app**, **Render**, or **AWS**.

### Production Features:

- **Optimized Tailwind**: CSS is built and minified during the Docker build stage.
- **Security**: Automatic SSL redirection and secure headers when `DEBUG=False`.
- **Static Files**: Efficiently served via **WhiteNoise**.
- **Containerized**: Runs anywhere that supports Docker.

For detailed deployment steps, see [DEPLOYMENT.md](./DEPLOYMENT.md).

---

## 🗄 Database Schema

The project uses a standard PostgreSQL database. Key models include:

- **Person**: Guests and members of the wedding party.
- **PersonGroup**: Groups guests together (e.g., households) so they can RSVP for each other.
- **RSVP**: Tracks attendance, dietary requirements, song suggestions, and Sunday meal plans.
- **Wedding/Venue**: Core event configuration.

---

## 🎨 Frontend Stack

- **Tailwind CSS**: Utility-first styling (Optimized via CLI in production).
- **Alpine.js**: Lightweight interactivity for form toggles and group switching.
- **HTMX**: For seamless, dynamic page updates without full refreshes.
