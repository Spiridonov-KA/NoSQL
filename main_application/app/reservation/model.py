from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class BookStatusEnum(str, Enum):
    # Состояние по умолчанию
    default = "default" 
    # Неоплачено
    unpaid = "unpaid"
    # Оплачено
    paid = "paid"


# Наследуемся от BaseModel, чтобы работала валидация
class ReservationSchema(BaseModel):
    id: str
    client_id: str
    room_id: str
    start_booking_date: datetime = None
    end_booking_date: datetime = None
    booking_status: BookStatusEnum = BookStatusEnum.default


class UpdateReservationSchema(BaseModel):
    client_id: str
    room_id: str
    start_booking_date: datetime = None
    end_booking_date: datetime = None
    booking_status: BookStatusEnum = BookStatusEnum.default
