
import uuid, time, secrets, string
from .redis_client import get_redis
from django.conf import settings

DEFAULT_TTL = settings.DEFAULT_TTL_SECONDS

def make_localpart(length=8):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def save_message(local, sender, subject, text, html=None, attachments=None, ttl=DEFAULT_TTL):
    r = get_redis()
    msgid = str(uuid.uuid4())
    msg_key = f"message:{msgid}"
    inbox_key = f"inbox:{local}"
    received_at = int(time.time())

    r.hset(msg_key, mapping={
        "from": sender,
        "to": local,
        "subject": subject or "",
        "text": text or "",
        "html": html or "",
        "received_at": received_at,
        "attachments": "" if not attachments else str(attachments)
    })
    r.expire(msg_key, ttl)

    r.lpush(inbox_key, msgid)
    r.expire(inbox_key, ttl)
    return msgid
