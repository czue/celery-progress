from channels.generic.websocket import AsyncWebsocketConsumer
import json

from celery.result import AsyncResult
from celery_progress.backend import Progress


class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']

        await self.channel_layer.group_add(
            self.task_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.task_id,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        task_type = text_data_json['type']

        if task_type == 'check_task_completion':
            await self.channel_layer.group_send(
                self.task_id,
                {
                    'type': 'update_task_progress',
                    'data': Progress(AsyncResult(self.task_id)).get_info()
                }
            )

    async def update_task_progress(self, event):
        data = event['data']

        await self.send(text_data=json.dumps(data))
