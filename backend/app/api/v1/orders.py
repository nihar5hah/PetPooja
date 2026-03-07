from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.voice_schemas import FailedOrderRetryOut, OrderOut
from app.services.order_service import list_orders
from app.services.voice_order_service import retry_failed_order


router = APIRouter(tags=["orders"])


@router.get("/orders", response_model=list[OrderOut])
def get_orders(
    restaurant_id: str = "default_restaurant",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return list_orders(db, restaurant_id, limit)


@router.post("/failed-orders/{queue_id}/retry", response_model=FailedOrderRetryOut)
def retry_failed(
    queue_id: int,
    db: Session = Depends(get_db),
):
    status, order_id, message = retry_failed_order(db, queue_id)
    return FailedOrderRetryOut(queue_id=queue_id, status=status, order_id=order_id, message=message)
