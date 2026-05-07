import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.businesses.models import Business
from apps.tenants.models import TeamMember


class InboxConsumer(AsyncWebsocketConsumer):
    @staticmethod
    async def _is_allowed(user, business_id: int) -> bool:
        if not user or not user.is_authenticated:
            return False
        owned = await sync_to_async(Business.objects.filter(id=business_id, owner=user).exists)()
        if owned:
            return True
        member = await sync_to_async(TeamMember.objects.filter(business_id=business_id, user=user, is_active=True).exists)()
        return member

    async def connect(self):
        business_id = self.scope['url_route']['kwargs']['business_id']
        allowed = await self._is_allowed(self.scope.get('user'), int(business_id))
        if not allowed:
            await self.close(code=4403)
            return
        self.group_name = f"inbox_{business_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def inbox_event(self, event):
        await self.send(text_data=json.dumps(event['payload']))
