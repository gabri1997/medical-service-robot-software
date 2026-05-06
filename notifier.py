import requests
from config import N8N_WEBHOOK_URL, NOTIFICATIONS_ENABLED


def notify_event(event_type: str, payload: dict | None = None) -> None:


    if not NOTIFICATIONS_ENABLED:
        return

    data = {
        "event_type": event_type,
        "payload": payload or {},
    }

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=data,
            timeout=3,
        )

        response.raise_for_status()

    except requests.RequestException as e:
        print(f"[notifier] Errore invio evento a n8n: {e}")