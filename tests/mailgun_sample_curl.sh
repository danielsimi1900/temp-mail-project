
#!/bin/bash
# Example curl to simulate Mailgun POST to the webhook (local testing)
curl -X POST http://127.0.0.1:8000/webhook/inbound/ \
  -F 'recipient=test@example.test' \
  -F 'sender=sender@example.com' \
  -F 'subject=Hello from curl' \
  -F 'stripped-text=This is a test message'
