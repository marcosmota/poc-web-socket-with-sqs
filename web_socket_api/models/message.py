from typing import Any
from dataclasses import dataclass

@dataclass
class Data:
    status: str
    message: str

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        _status = str(obj.get("status"))
        _message = str(obj.get("message"))
        return Data(_status, _message)

@dataclass
class Metadata:
    channel: str
    broadcast: bool
    user_id: str

    @staticmethod
    def from_dict(obj: Any) -> 'Metadata':
        _channel = str(obj.get("channel"))
        _user_id = str(obj.get("user_id"))
        _broadcast = bool(obj.get("broadcast"))
        return Metadata(_channel, _broadcast, _user_id)

@dataclass
class Message:
    metadata: Metadata
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> 'Message':
        _metadata = Metadata.from_dict(obj.get("metadata"))
        _data = Data.from_dict(obj.get("data"))
        return Message(_metadata, _data)