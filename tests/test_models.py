import pytest
from src.common.models import OrderEvent
from datetime import datetime, timezone

def test_order_event_ok():
    evt = OrderEvent(
        event_type="order_created",
        event_ts=datetime.now(timezone.utc),
        order_id="ord_1",
        customer_id="cus_1",
        status="PLACED",
        amount=10.0,
        currency="USD",
        items_count=1,
    )
    assert evt.amount == 10.0

def test_items_count_must_be_positive():
    import pytest
    from datetime import datetime, timezone
    with pytest.raises(Exception):
        OrderEvent(
            event_type="order_created",
            event_ts=datetime.now(timezone.utc),
            order_id="ord_1",
            customer_id="cus_1",
            status="PLACED",
            amount=10.0,
            currency="USD",
            items_count=0,
        )

def test_negative_amount_raises_error():
    from src.common.models import OrderEvent

    with pytest.raises(Exception):
        OrderEvent(
            event_type="order_created",
            event_ts=datetime.now(timezone.utc),
            order_id="ord_999",
            customer_id="cus_999",
            status="PLACED",
            amount=-50.0,  # invalid
            currency="USD",
            items_count=1,
        )

