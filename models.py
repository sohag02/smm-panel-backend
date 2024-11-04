from pydantic import BaseModel, ValidationError, model_validator
from typing import TypedDict
from enum import Enum

class Order(BaseModel):
    order_id: int
    service_id: int

class YoutubeConfig(Order):
    username: str

class FacebookConfig(Order):
    username: str | None = None
    accounts: int
    watch_time: int
    range: int
    interval: int
    likes: int
    comments: int
    subscribes: int
    shares: int
    livestream_link: str | None = None
    threads: int

    @model_validator(mode='after')
    def check_username_or_livestream_link(self):
        username, livestream_link = self.username, self.livestream_link
        if not (username or livestream_link):
            raise ValidationError('Either username or livestream_link must be present. None were supplied.')
        if username and livestream_link:
            raise ValidationError('Only one of username or livestream_link must be present. Both were supplied.')
        return self

class Service(TypedDict):
    id: int
    name: str
    description: str
    price: int

class Order(TypedDict):
    id: int
    service_id: int
    user_id: str
    status: str
    added_at: str
    cost: int

class OrderStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"