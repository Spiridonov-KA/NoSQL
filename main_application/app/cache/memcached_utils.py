from pymemcache import HashClient
from pymemcache.client.base import Client
import os

from app.cache.json_serializer import JsonSerializer

memcached_client: Client = None
memcached_room: Client = None
memcached_reservation: Client = None


def get_memcached_client() -> Client:
    return memcached_client


def get_memcached_room() -> Client:
    return memcached_room


def get_memcached_reservation() -> Client:
    return memcached_reservation


def connect_and_init_memcached():
    global memcached_client
    global memcached_room
    global memcached_reservation
    memcached_client_uri = os.getenv('MEMCACHED_CLIENT_URI')
    memcached_room_uri = os.getenv('MEMCACHED_ROOM_URI')
    memcached_reservation_uri = os.getenv('MEMCACHED_RESERVATION_URI')

    try:
        memcached_client = HashClient(memcached_client_uri.split(','), serde=JsonSerializer())
        print(f'Connected to memcached(client) with uri {memcached_client_uri}')
    except Exception as ex:
        print(f'Cant connect to memcached(client): {ex}')

    try:
        memcached_room = HashClient(memcached_room_uri.split(','), serde=JsonSerializer())
        print(f'Connected to memcached(room) with uri {memcached_room_uri}')
    except Exception as ex:
        print(f'Cant connect to memcached(room): {ex}')

    try:
        memcached_reservation = HashClient(memcached_reservation_uri.split(','), serde=JsonSerializer())
        print(f'Connected to memcached(reservation) with uri {memcached_reservation_uri}')
    except Exception as ex:
        print(f'Cant connect to memcached(reservation): {ex}')


def close_memcached_connect():
    global memcached_client
    global memcached_room
    global memcached_reservation
    
    if memcached_client is None:
        return
    memcached_client.close()

    if memcached_room is None:
        return
    memcached_room.close()

    if memcached_reservation is None:
        return
    memcached_reservation.close()
