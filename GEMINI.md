
# Gemini Code Assistant Context

## Project Overview

This is a minimal Django project for a temporary email service (like a 10-minute mail). It's designed to receive emails via a Mailgun webhook, store them ephemerally in Redis, and expose them through a simple REST API.

The project is structured as a standard Django application with a single app named `mailtemp`.

### Key Technologies

*   **Backend:** Django, Django Rest Framework
*   **Data Storage:** Redis (for ephemeral email storage), SQLite (for Django's own needs)
*   **Email Handling:** Mailgun (for inbound email routing via webhooks)
*   **Dependencies:** `python-dotenv` (for managing environment variables), `bleach` (for HTML sanitization)

### Architecture

1.  **Inbound Email:** Mailgun is configured to forward incoming emails to the `/webhook/inbound/` endpoint.
2.  **Webhook Handler:** The `inbound_webhook` view in `mailtemp/views.py` handles the incoming POST request from Mailgun. It verifies the Mailgun signature for security.
3.  **Redis Storage:** The `mail_utils.py` module handles saving the email content into Redis. Each message and inbox has a Time-To-Live (TTL), ensuring the data is temporary.
4.  **API Endpoints:** The `mailtemp/urls.py` and `mailtemp/views.py` define REST endpoints to:
    *   Generate a new temporary email address (`/api/generate/`).
    *   List messages for an inbox (`/api/inbox/<local>/`).
    *   Fetch the details of a specific message (`/api/message/<msgid>/`).
5.  **Frontend:** A very basic frontend is served from `templates/index.html`, which can be used to generate addresses and test the service.

## Building and Running

### 1. Prerequisites

*   Python 3.x
*   Redis server
*   A Mailgun account (for production)

### 2. Setup and Installation

1.  **Create and activate a Python virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**

    Create a `.env` file in the project root. See `.env.example` for the required variables.

    ```
    DJANGO_SECRET_KEY=your-secret-key
    MAILGUN_API_KEY=your-mailgun-api-key
    REDIS_URL=redis://127.0.0.1:6379/0
    DOMAIN_NAME=your-domain.com
    ```

### 3. Running the Application

1.  **Run database migrations:**

    ```bash
    python manage.py migrate
    ```

2.  **Start the Django development server:**

    ```bash
    python manage.py runserver
    ```

    The application will be available at `http://127.0.0.1:8000`.

### 4. Testing

*   A sample cURL command for testing the Mailgun webhook is provided in `tests/mailgun_sample_curl.sh`.

## Development Conventions

*   **Configuration:** Application settings are managed through environment variables loaded via `python-dotenv`. Default values are provided in `config/settings.py` for development.
*   **Code Style:** The code follows standard Django and Python conventions.
*   **Security:**
    *   Mailgun webhook signatures are verified to prevent unauthorized POST requests.
    *   HTML content in emails is sanitized using `bleach` to prevent XSS attacks.
    *   A simple rate-limiting middleware is implemented in `mailtemp/middleware.py`.
