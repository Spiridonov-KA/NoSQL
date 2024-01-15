from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pymemcache import HashClient

from app.cache.memcached_utils import get_memcached_room

from app.room.model import *
from app.room.repository_elasticsearch import *
from app.room.repository_mongo import *

room_router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
    responses={404: {"description": "Not found"}},
)


@room_router.get(
    "/"
)
async def get_all_room(mongo_repository: RoomMongoRepository
                       = Depends(RoomMongoRepository.mongo_room_factory)) -> list[RoomSchema]:
    return await mongo_repository.get_all()


@room_router.get(
    "/{room_id}",
    response_description="Get a single room by id"
)
async def room_by_id(room_id: str,
                     mongo_repository: RoomMongoRepository = Depends(RoomMongoRepository.mongo_room_factory),
                     memcached_hash_room: HashClient = Depends(get_memcached_room)):
    if not ObjectId.is_valid(room_id):
        raise HTTPException(status_code=400, detail='Bad Request')
    
    room = memcached_hash_room.get(room_id)
    if room is not None:
        return {"room": room}

    if (room := await mongo_repository.get_room(room_id)) is not None:
        return {"room": room}
    
    raise HTTPException(status_code=404, detail=f'Room with ID : {room_id} not found')


@room_router.post(
    "/",
    response_description="New room id"
)
async def room_add(room: UpdateRoomSchema,
                   mongo_repository: RoomMongoRepository = Depends(RoomMongoRepository.mongo_room_factory),
                   es_repository: RoomEsRepository = Depends(RoomEsRepository.es_room_factory)):
    if (room_id := await mongo_repository.add_room(room)) is not None:
        await es_repository.create(room_id, room)
        return {"room_id": room_id}
    
    raise HTTPException(status_code=404, detail=f'Room with ID : {room_id} already exists')


@room_router.put(
    "/{room_id}",
    response_description="Updated a single room"
)
async def room_update(room_id: str,
                      room: UpdateRoomSchema,
                      mongo_repository: RoomMongoRepository = Depends(RoomMongoRepository.mongo_room_factory),
                      es_repository: RoomEsRepository = Depends(RoomEsRepository.es_room_factory)):
    if not ObjectId.is_valid(room_id):
        raise HTTPException(status_code=400, detail='Bad Request')

    if (room_upd := await mongo_repository.update_room(room_id, room)) is not None:
        await es_repository.update(room_id, room)
        return {"room_upd": room_upd}
    
    raise HTTPException(status_code=404, detail=f'Room with ID : {room_id} already exists')


@room_router.get(
    "/city/{city_name}",
    response_description="All rooms available in the given city"
)
async def list_available_rooms_city(city_name: str,
                                    es_repository: RoomEsRepository = Depends(RoomEsRepository.es_room_factory)):
    if (rooms := await es_repository.find_by_city(city_name)) is not None:
        return {"rooms": rooms}
    
    raise HTTPException(status_code=404, detail=f'No available rooms in the given city: {city_name}')


@room_router.get(
    "/country/{country_name}",
    response_description="All rooms available in the given country"
)
async def list_available_rooms_country(country_name: str,
                                       es_repository: RoomEsRepository = Depends(RoomEsRepository.es_room_factory)):
    if (rooms := await es_repository.find_by_country(country_name)) is not None:
        return {"rooms": rooms}
    
    raise HTTPException(status_code=404, detail=f'No available rooms in the given country: {country_name}')


@room_router.get(
    "/attributes/{attribute}",
    response_description="All rooms available with the given attribute"
)
async def list_available_rooms_attributes(attribute: str,
                                          es_repository: RoomEsRepository = Depends(RoomEsRepository.es_room_factory)):
    attribute = attribute.replace('%2B', ' ')  # reformat the attribute string
    if (rooms := await es_repository.find_by_attribute(attribute)) is not None:
        return {"rooms": rooms}
    
    raise HTTPException(status_code=404, detail=f'No available rooms in the given attribute: {attribute}')
