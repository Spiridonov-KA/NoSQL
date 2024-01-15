from __future__ import annotations

import os
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from app.client.model import *
from app.reservation.model import *
from app.room.model import *

db_client: AsyncIOMotorClient = None


async def get_db_collection() -> AsyncIOMotorCollection:
    mongo_db = os.getenv('MONGO_DB')
    mongo_collection = os.getenv('MONGO_COLLECTION')
    print(f'{mongo_collection}')
    return db_client.get_database(mongo_db).get_collection(mongo_collection)


async def get_mongo_client() -> AsyncIOMotorCollection:
    mongo_db = os.getenv('MONGO_DB')
    mongo_collection_client = os.getenv('MONGO_COLLECTION_CLIENT')
    print(f'{mongo_collection_client}')
    return db_client.get_database(mongo_db).get_collection(mongo_collection_client)


async def get_mongo_room() -> AsyncIOMotorCollection:
    mongo_db = os.getenv('MONGO_DB')
    mongo_collection_room = os.getenv('MONGO_COLLECTION_ROOM')
    print(f'{mongo_collection_room}')
    return db_client.get_database(mongo_db).get_collection(mongo_collection_room)


async def get_mongo_reservation() -> AsyncIOMotorCollection:
    mongo_db = os.getenv('MONGO_DB')
    mongo_collection_reservation = os.getenv('MONGO_COLLECTION_RESERVATION')
    print(f'{mongo_collection_reservation}')
    return db_client.get_database(mongo_db).get_collection(mongo_collection_reservation)


async def connect_and_init_mongo():
    global db_client
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db = os.getenv('MONGO_DB')
    mongo_collection = os.getenv('MONGO_COLLECTION')
    mongo_collection_room = os.getenv('MONGO_COLLECTION_ROOM')
    mongo_collection_client = os.getenv('MONGO_COLLECTION_CLIENT')
    mongo_collection_reservation = os.getenv('MONGO_COLLECTION_RESERVATION')
    try:
        db_client = AsyncIOMotorClient(mongo_uri)
        await db_client.server_info()
        print(f'Connected to mongo with uri {mongo_uri}')
        if mongo_db not in await db_client.list_database_names():
            await db_client\
                .get_database(mongo_db)\
                .create_collection(mongo_collection)
            await db_client\
                .get_database(mongo_db)\
                .create_collection(mongo_collection_client)
            await db_client\
                .get_database(mongo_db)\
                .create_collection(mongo_collection_room)
            await db_client\
                .get_database(mongo_db)\
                .create_collection(mongo_collection_reservation)
            print(f'Database {mongo_db} created')

    except Exception as ex:
        print(f'Cant connect to mongo: {ex}')


async def close_db_connect():
    global db_client
    if db_client is None:
        return
    db_client.close()


def get_filter(id: str) -> dict:
    return {'_id': ObjectId(id)}


def map_client(client: Any) -> ClientSchema | None:
    if client is None:
        return None
    return ClientSchema(id=str(client['_id']), name=client['name'], email=client['email'])


def map_rooms(room: Any) -> RoomSchema | None:
    if room is None:
        return None
    return RoomSchema(id=str(room['_id']), full_address=Address(country=room['full_address']['country'],
                                                                city=room['full_address']['city'],
                                                                address=room['full_address']['address']),
                      description=room['description'], attributes=room['attributes'])


def map_reservation(reservation: Any) -> ReservationSchema | None:
    if reservation is None:
        return None
    return ReservationSchema(id=str(reservation['_id']), client_id=reservation['client_id'],
                             room_id=reservation['room_id'],
                             start_booking_date=reservation['start_booking_date'],
                             end_booking_date=reservation['end_booking_date'],
                             booking_status=reservation['booking_status'])
