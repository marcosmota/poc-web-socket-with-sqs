
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections = []

    async def connect(self, channel: str, user_id: str, connection: WebSocket):
        self.active_connections.append({
            'user_id': user_id,
            'channel': channel,
            'websocket': connection
        })
        await connection.accept()

    async def disconnect(self, channel: str, user_id: str):
        self.active_connections = list(filter(lambda conn: conn['user_id'] != user_id or conn['channel'] != channel, self.active_connections))

    def get_connections_by_user(self, channel: str, user_id: str):
        return list(filter(lambda conn: conn['user_id'] == user_id and conn['channel'] == channel, self.active_connections))
    
    def get_connections_by_channel(self, channel: str):
        return list(filter(lambda conn: conn['channel'] == channel, self.active_connections))
    
    def set_living_connections(self, user_id: str, channel: str, connections):
        self.active_connections[user_id][channel] = connections