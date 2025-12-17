
# Temp Mail Project (Minimal Django skeleton)

This is a minimal Django project skeleton for a temporary email (10-minute) service.
It includes:
- Django + DRF endpoints for inbox/message listing
- Mailgun webhook receiver with signature verification
- Redis-backed ephemeral storage (TTL based)
- Basic frontend (single page) that can generate addresses client-side for testing
- Simple rate-limiter middleware using Redis counters
- HTML sanitization using `bleach`

## Quick start (local testing)

1. Create Python virtual environment and install requirements:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run Redis (e.g., locally with Docker):
```bash
docker run --rm -p 6379:6379 redis:7
```

3. Set environment variables (create a `.env` file or export in shell):
- `DJANGO_SECRET_KEY` - secret key for Django
- `MAILGUN_API_KEY` - your Mailgun API key (for webhook verification; for local testing you can set any string)
- `REDIS_URL` - e.g. redis://127.0.0.1:6379/0
- `DOMAIN_NAME` - your domain for addresses (e.g., example.test)

Example `.env`:
```
DJANGO_SECRET_KEY=replace_me
MAILGUN_API_KEY=replace_me
REDIS_URL=redis://127.0.0.1:6379/0
DOMAIN_NAME=example.test
```

4. Run migrations and start server:
```bash
python manage.py migrate
python manage.py runserver
```

5. Test webhook locally by POSTing a Mailgun-like payload to:
`http://127.0.0.1:8000/webhook/inbound/`

(See `tests/mailgun_sample_curl.sh` for an example curl payload.)

## Production notes
- Use HTTPS and a proper domain.
- Set MX records in DNS and configure Mailgun inbound routes to POST to `/webhook/inbound/`.
- Use real Mailgun API key and verify signatures.
- Add CAPTCHA and stronger rate-limiting before public launch.
- Monitor domain reputation and abuse.

