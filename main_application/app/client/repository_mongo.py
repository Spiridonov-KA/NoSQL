from __future__ import annotations

from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorCollection

from app.client.model import *
from app.repository.mongo_utils import *


class ClientMongoRepository:
    _mongo_collection: AsyncIOMotorCollection

    def __init__(self, mongo_collection: AsyncIOMotorCollection):
        self._mongo_collection = mongo_collection

    @staticmethod
    def mongo_client_factory(mongo_collection: AsyncIOMotorCollection = Depends(get_mongo_client)):
        return ClientMongoRepository(mongo_collection)
    
    async def get_all(self) -> list[ClientSchema]:
        db_client = []
        async for client in self._mongo_collection.find():
            db_client.append(map_client(client))
        print(f'Get all clients from mongo')
        return db_client

    async def get_client(self,
                         client_id: str) -> ClientSchema | None:
        db_client = await self._mongo_collection.find_one(get_filter(client_id))
        print(f'Get client {client_id} from mongo')
        return map_client(db_client)

    async def add_client(self,
                         client: UpdateClientSchema) -> str:
        insert_result = await self._mongo_collection.insert_one(dict(client))
        print(f'App client {insert_result.inserted_id} from mongo')
        return str(insert_result.inserted_id)

    async def update_client(self,
                            client_id: str,
                            client: UpdateClientSchema) -> ClientSchema | None:
        db_client = await self._mongo_collection.find_one_and_replace(get_filter(client_id), dict(client))
        print(f'Update client {client_id} from mongo')
        return map_client(db_client)

    async def delete_client(self,
                            client_id: str) -> ClientSchema | None:
        db_client = await self._mongo_collection.find_one_and_delete(get_filter(client_id))
        print(f'Delete client {client_id} from mongo')
        return map_client(db_client)
