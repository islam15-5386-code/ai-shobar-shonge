from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def publish_inbox_event(business_id: int, payload: dict) -> None:
    layer = get_channel_layer()
    if not layer:
        return
    async_to_sync(layer.group_send)(
        f"inbox_{business_id}",
        {"type": "inbox.event", "payload": payload},
    )
