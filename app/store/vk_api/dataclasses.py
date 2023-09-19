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
