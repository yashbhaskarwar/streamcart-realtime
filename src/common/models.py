from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal
from decimal import Decimal
import uuid

OrderStatus = Literal["PLACED", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]

class OrderEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: Literal["order_created", "order_updated", "order_cancelled"]
    event_ts: datetime
    order_id: str
    customer_id: str
    status: OrderStatus
    amount: Decimal
    currency: Literal["USD","EUR","GBP","INR"]
    items_count: int

    @field_validator("amount")
    @classmethod
    def non_negative_amount(cls, v):
        if v < 0:
            raise ValueError("amount must be non-negative")
        return v

    @field_validator("items_count")
    @classmethod
    def positive_items(cls, v):
        if v <= 0:
            raise ValueError("items_count must be >= 1")
        return v
    
    def __str__(self) -> str:
        return f"Order {self.order_id} [{self.status}] {self.currency} {self.amount}"

