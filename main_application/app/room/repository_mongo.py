from __future__ import annotations

from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorCollection

from app.room.model import *
from app.repository.mongo_utils import *


class RoomMongoRepository:
    _mongo_collection: AsyncIOMotorCollection

    def __init__(self, mongo_collection: AsyncIOMotorCollection):
        self._mongo_collection = mongo_collection

    @staticmethod
    def mongo_room_factory(mongo_collection: AsyncIOMotorCollection = Depends(get_mongo_room)):
        return RoomMongoRepository(mongo_collection)

    async def get_all(self) -> list[RoomSchema]:
        db_rooms = []
        async for room in self._mongo_collection.find():
            db_rooms.append(map_rooms(room))
        print(f'Get all rooms from mongo')
        return db_rooms

    async def get_room(self, room_id: str) -> RoomSchema | None:
        db_rooms = await self._mongo_collection.find_one(get_filter(room_id))
        print(f'Get room {room_id} from mongo')
        return map_rooms(db_rooms)

    async def add_room(self,
                       room: UpdateRoomSchema) -> str:
        insert_result = await self._mongo_collection.insert_one(dict(room))
        print(f'Add room {insert_result.inserted_id} from mongo')
        return str(insert_result.inserted_id)

    async def update_room(self,
                    room_id: str,
                    room: UpdateRoomSchema) -> RoomSchema | None:
        db_rooms = await self._mongo_collection.find_one_and_replace(get_filter(room_id), dict(room))
        print(f'Update room {room_id} from mongo')
        return map_rooms(db_rooms)

    async def delete_room(self,
                    room_id: str) -> RoomSchema | None:
        db_rooms = await self._mongo_collection.find_one_and_delete(get_filter(room_id))
        print(f'Delete room {room_id} from mongo')
        return map_rooms(db_rooms)
