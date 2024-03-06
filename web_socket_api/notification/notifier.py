import os
from typing import List
from starlette.websockets import WebSocket
from web_socket_api.models.message import Message

from web_socket_api.communication.implementations.sqs import SQSSubscriber
import boto3

from web_socket_api.notification.connection_manager import ConnectionManager

class Notifier:
    def __init__(
        self, connection_manager: ConnectionManager
    ) -> None:
        self.connections: List[WebSocket] = []
        self.connection_manager = connection_manager
        session = boto3.Session()
        self.subscriber = SQSSubscriber(session)
        self.is_ready = False
        self.queue_url = os.getenv("QUEUE_URL")

    async def setup(self):
        self.is_ready = True
        for message in self.subscriber.subscribe(to=self.queue_url):
            await self._notify(Message.from_dict(message))

    async def _notify(self, message: Message):
        if message.metadata.broadcast:
            await self._broadcast_message(message)
        else:
            await self._send_message(message)

    async def _send_message(self, message: Message):
        connections = self.connection_manager.get_connections_by_user(
            channel=message.metadata.channel,
            user_id=message.metadata.user_id
        )

        while len(connections) > 0:
            connection = connections.pop()
            websocket = connection['websocket']
            await websocket.send_text(f"{message.data.__dict__}")

    async def _broadcast_message(self, message: Message):
        connections = self.connection_manager.get_connections_by_channel(message.metadata.channel)
        living_connections = []
        while len(connections) > 0:
            connection = connections.pop()
            websocket = connection['websocket']
            await websocket.send_text(f"{message.data.__dict__}")
            living_connections.append(websocket)
