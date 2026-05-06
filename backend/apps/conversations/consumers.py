import json

from channels.generic.websocket import AsyncWebsocketConsumer


class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        business_id = self.scope['url_route']['kwargs']['business_id']
        self.group_name = f"inbox_{business_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def inbox_event(self, event):
        await self.send(text_data=json.dumps(event['payload']))
