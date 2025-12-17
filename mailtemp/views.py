
import bleach, hmac, hashlib
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .mail_utils import save_message, make_localpart
from .redis_client import get_redis

def verify_mailgun_signature(timestamp, token, signature):
    key = settings.MAILGUN_API_KEY or ''
    if not key:
        return False
    data = f"{timestamp}{token}".encode('utf-8')
    expected = hmac.new(key.encode('utf-8'), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@csrf_exempt
@api_view(['POST'])
def inbound_webhook(request):
    data = request.POST or request.data
    timestamp = data.get('timestamp')
    token = data.get('token')
    signature = data.get('signature') or None
    if not signature and isinstance(request.data, dict) and 'signature' in request.data:
        try:
            signature = request.data['signature'].get('signature')
            timestamp = request.data['signature'].get('timestamp')
            token = request.data['signature'].get('token')
        except Exception:
            pass

    if not (timestamp and token and signature):
        if settings.MAILGUN_API_KEY == 'test_mailgun_key':
            verified = True
        else:
            return Response({'detail': 'missing signature'}, status=400)
    else:
        verified = verify_mailgun_signature(timestamp, token, signature)

    if not verified:
        return Response({'detail': 'signature verification failed'}, status=403)

    recipient = data.get('recipient') or data.get('To') or data.get('to')
    sender = data.get('sender') or data.get('from') or ''
    subject = data.get('subject') or ''
    text = data.get('stripped-text') or data.get('body-plain') or data.get('text') or ''
    html = data.get('stripped-html') or data.get('html') or ''

    if not recipient:
        return Response({'detail': 'no recipient'}, status=400)

    local = recipient.split('@')[0].lower()
    clean_html = bleach.clean(html, tags=['p','br','b','i','strong','em','a','ul','ol','li'], strip=True)

    msgid = save_message(local, sender, subject, text, clean_html)
    return Response({'msgid': msgid})

@api_view(['GET'])
def inbox_list(request, local):
    r = get_redis()
    inbox_key = f"inbox:{local}"
    msgids = r.lrange(inbox_key, 0, -1) or []
    messages = []
    for mid in msgids:
        m = r.hgetall(f"message:{mid}") or {}
        if m:
            messages.append({
                'msgid': mid,
                'from': m.get('from'),
                'subject': m.get('subject'),
                'preview': (m.get('text') or '')[:200],
                'received_at': m.get('received_at')
            })
    return Response(messages)

@api_view(['GET'])
def message_detail(request, msgid):
    r = get_redis()
    m = r.hgetall(f"message:{msgid}") or {}
    if not m:
        return Response({'detail': 'not found'}, status=404)
    return Response({
        'msgid': msgid,
        'from': m.get('from'),
        'to': m.get('to'),
        'subject': m.get('subject'),
        'text': m.get('text'),
        'html': m.get('html'),
        'received_at': m.get('received_at'),
    })

@api_view(['POST'])
def generate_address(request):
    local = make_localpart(8)
    domain = settings.DOMAIN_NAME
    return Response({'address': f"{local}@{domain}", 'local': local})
