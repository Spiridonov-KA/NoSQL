from __future__ import annotations

from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorCollection

from app.repository.mongo_utils import *
from app.reservation.model import *


class ReservationMongoRepository:
    _mongo_collection: AsyncIOMotorCollection

    def __init__(self, mongo_collection: AsyncIOMotorCollection):
        self._mongo_collection = mongo_collection

    @staticmethod
    def mongo_reservation_factory(mongo_collection: AsyncIOMotorCollection = Depends(get_mongo_reservation)):
        return ReservationMongoRepository(mongo_collection)
    
    async def get_all(self) -> list[ReservationSchema]:
        db_reservation = []
        async for reservation in self._mongo_collection.find():
            db_reservation.append(map_reservation(reservation))
        print(f'Get all reservations from mongo')
        return db_reservation

    async def get_all_reservations_by_client_id(self,
                                                client_id: str) -> list[ReservationSchema]:
        db_reservation = []
        async for reservation in self._mongo_collection.find({'_id': client_id}):
            db_reservation.append(map_reservation(reservation))
        print(f'Get all reservations by client id: {client_id} from mongo')
        return [ReservationSchema()]

    async def get_reservation(self,
                              reservation_id: str) -> ReservationSchema | None:
        db_reservation = await self._mongo_collection.find_one(get_filter(reservation_id))
        print(f'Get reservation {reservation_id} from mongo')
        return map_reservation(db_reservation)

    async def add_reservation(self,
                              reservation: UpdateReservationSchema) -> str:
        insert_result = await self._mongo_collection.insert_one(dict(reservation))
        print(f'Add reservation {insert_result.inserted_id} from mongo')
        return str(insert_result.inserted_id)

    async def update_reservation(self,
                                 reservation_id: str,
                                 reservation: UpdateReservationSchema) -> ReservationSchema | None:
        db_reservation = await self._mongo_collection.find_one_and_replace(get_filter(reservation_id), dict(reservation))
        print(f'Update reservation {reservation_id} from mongo')
        return map_reservation(db_reservation)

    async def delete_reservation(self,
                                 reservation_id: str) -> ReservationSchema | None:
        db_reservation = await self._mongo_collection.find_one_and_delete(get_filter(reservation_id))
        print(f'Delete reservation {reservation_id} from mongo')
        return map_reservation(db_reservation)
