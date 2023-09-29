from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    peer_id: Optional[int]
    user_id: Optional[int]
    text: str


@dataclass
class UpdateMessage:
    peer_id: int
    from_id: int
    text: str
    id: int


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class UpdateEventMessage:
    user_id: int
    event_id: str
    payload: str
    peer_id: int


@dataclass
class UpdateEventObject:
    event_message: UpdateEventMessage


@dataclass
class UpdateEvent:
    type: str
    event_object: UpdateEventObject
