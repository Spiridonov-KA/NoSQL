import time

from fastapi import APIRouter, HTTPException
from pymemcache import HashClient

from app.cache.memcached_utils import get_memcached_reservation
from app.reservation.lock_redis import RedisLock

from app.reservation.repository_elasticsearch import *
from app.reservation.repository_mongo import *
from app.client.repository_mongo import *
from app.room.repository_mongo import *

# Создаём router
reservation_router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={404: {"description": "Not found"}},
)


@reservation_router.get(
    "/"
)
async def get_all_reservation(mongo_repository: ReservationMongoRepository
                              = Depends(ReservationMongoRepository.mongo_reservation_factory)) -> list[ReservationSchema]:
    return await mongo_repository.get_all()


@reservation_router.get(
    "/{reservation_id}",
    response_description="Single reservation with given ID"
)
async def reservation_by_id(reservation_id: str,
                            mongo_repository: ReservationMongoRepository
                            = Depends(ReservationMongoRepository.mongo_reservation_factory), 
                            memcached_hash_reservation: HashClient = Depends(get_memcached_reservation)):
    if not ObjectId.is_valid(reservation_id):
        raise HTTPException(status_code=400, detail='Bad Request')
    
    reservation = memcached_hash_reservation.get(reservation_id)
    if reservation is not None:
        return {"reservation": reservation}
    
    if (reservation := await mongo_repository.get_reservation(reservation_id)) is not None:
        return {"reservation": reservation}
    
    raise HTTPException(status_code=404, detail=f'Reservation with ID : {reservation_id} not found')


@reservation_router.get(
    "/clients/{client_id}",
    response_description="All reservations for given client"
)
async def reservations_by_client_id(client_id: str,
                                    es_repository: ReservationEsRepository = Depends(
                                        ReservationEsRepository.es_reservation_factory)):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail='Bad Request')

    if (reservations := await es_repository.find_by_client_id(client_id)) is not None:
        return {"reservations": reservations}

    raise HTTPException(status_code=404, detail=f'No such client with ID: {client_id}')


@reservation_router.get(
    "/rooms/{room_id}",
    response_description="All reservations for this room"
)
async def reservations_by_room_id(room_id: str,
                                  es_repository: ReservationEsRepository = Depends(
                                      ReservationEsRepository.es_reservation_factory)):
    if not ObjectId.is_valid(room_id):
        raise HTTPException(status_code=400, detail='Bad Request')

    if len((reservations := await es_repository.find_by_room_id(room_id))):
        return {"reservations": reservations}

    raise HTTPException(status_code=404, detail=f'No such room with ID: {room_id}')


@reservation_router.get(
    "/from/{time_from}/to/{time_to}",
    response_description="All reservations in the given period"
)
async def reservations_from_to(time_from: datetime,
                               time_to: datetime,
                               es_repository: ReservationEsRepository = Depends(
                                   ReservationEsRepository.es_reservation_factory)):
    if len((reservations := await es_repository.find_by_range(time_from, time_to))):
        return {"reservations": reservations}

    raise HTTPException(status_code=404, detail=f'No reservations in this period: from {time_from}, to {time_to}')


@reservation_router.post(
    "/",
    response_description="Added reservation ID"
)
async def reservation_add(reservation: UpdateReservationSchema,
                          mongo_repository: ReservationMongoRepository
                          = Depends(ReservationMongoRepository.mongo_reservation_factory),
                          mongo_repository_client: ClientMongoRepository
                          = Depends(ClientMongoRepository.mongo_client_factory),
                          mongo_repository_room: RoomMongoRepository
                          = Depends(RoomMongoRepository.mongo_room_factory),
                          es_repository: ReservationEsRepository
                          = Depends(ReservationEsRepository.es_reservation_factory),
                          redis_lock: RedisLock = Depends(RedisLock.redis_reservation_factory)):
    if (not(client := await mongo_repository_client.get_client(str(reservation.client_id)))):
        raise HTTPException(status_code=404, detail=f'Client with ID : {reservation.client_id} not found')
    
    if (not(room := await mongo_repository_room.get_room(str(reservation.room_id)))):
        raise HTTPException(status_code=404, detail=f'Room with ID : {reservation.room_id} not found')

    while i := 3 > 0:
        # Проверяем забранирована ли комната в указанную дату.
        # Если есть пересечение дат, то бросаем ошибку 404 и дату, на которую зарезервинована комнату

        if es_repository.find_intersection(reservation.room_id,
                                           reservation.start_booking_date, reservation.end_booking_date) != 0:
            raise HTTPException(status_code=404, detail=f'Room with ID : {reservation.room_id}'
                                                        f' is occupied for some of chosen days')

        # Получаем блокировщик
        lock = redis_lock.get_lock(reservation.room_id)
        if lock.acquire():
            # Если нет пересечения, то добавляем бронирование в mongodb и elastic
            if (reservation_id := await mongo_repository.add_reservation(reservation)) is not None:
                await es_repository.create(reservation_id, reservation)

            reservation.booking_status = BookStatusEnum.paid
            await mongo_repository.update_reservation(reservation_id, reservation)
            await es_repository.update(reservation_id, reservation)

            lock.release()
            return {"reservation_id": reservation_id}
        else:
            time.sleep(0.5)
            i -= 1


@reservation_router.put(
    "/{reservation_id}",
    response_description="Updated reservation"
)
async def reservation_update(reservation_id: str,
                             reservation_upd: UpdateReservationSchema,
                             mongo_repository: ReservationMongoRepository = Depends(ReservationMongoRepository.mongo_reservation_factory),
                             mongo_repository_client: ClientMongoRepository = Depends(ClientMongoRepository.mongo_client_factory),
                             mongo_repository_room: RoomMongoRepository = Depends(RoomMongoRepository.mongo_room_factory),
                             es_repository: ReservationEsRepository = Depends(ReservationEsRepository.es_reservation_factory)):
    if not ObjectId.is_valid(reservation_id):
        raise HTTPException(status_code=400, detail='Bad Request')
    
    if (not(client := await mongo_repository_client.get_client(str(reservation_upd.client_id)))):
        raise HTTPException(status_code=404, detail=f'Client with ID : {reservation_upd.client_id} not found')
    
    if (not(room := await mongo_repository_room.get_room(str(reservation_upd.room_id)))):
        raise HTTPException(status_code=404, detail=f'Room with ID : {reservation_upd.room_id} not found')

    if es_repository.find_upd_intersection(reservation_id, reservation_upd.room_id,
                                           reservation_upd.start_booking_date, reservation_upd.end_booking_date) == 0:
        raise HTTPException(status_code=404, detail=f'Room with ID : {reservation_id}'
                                                    f' is occupied for some of chosen days')

    if (reservation := await mongo_repository.update_reservation(reservation_id, reservation_upd)) is not None:
        await es_repository.update(reservation_id, reservation_upd)
        return {"updated_reservation": reservation}

    raise HTTPException(status_code=404, detail=f'Reservation with ID : {reservation_id} not found')
