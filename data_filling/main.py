import csv
import random
import asyncio

import requests

from models.client_model import *
from models.room_model import *

LENGTH = 300


def test_can_call_endpoint_rooms():
    response = requests.get("http://localhost:80/rooms")
    assert response.status_code == 200


def letters(name):
    return ''.join(filter(str.isalpha, name))


async def fill_clients():
    clients = []
    with open("dump_data/Users.csv", encoding='utf-8') as r_file:
        file_reader = csv.DictReader(r_file, delimiter=",")
        count = 0
        for row in file_reader:
            if count == 0:
                print(f'{", ".join(row)}')
            client = UpdateClientSchema(name=str(row["DisplayName"]),
                                        email=str(letters(row["DisplayName"]) + str(row["Id"]) + "@gmail.com"))
            print(f"{count}: {client}")
            clients.append(client)
            count += 1
            if count == LENGTH:
                break
    return clients


async def fill_rooms():
    rooms = []
    with open("dump_data/Rooms_auckland_dump.csv", encoding='utf-8') as r_file:
        file_reader = csv.DictReader(r_file, delimiter=",")
        count = 0
        for row in file_reader:
            if count == 0:
                print(f'{", ".join(row)}')
            room = UpdateRoomSchema(
                description=str("Overall Satisfaction " + str(row["overall_satisfaction"])),
                attributes=str(row["room_type"]),
                full_address=Address(country="NewZealand", city="Auckland", address=str(row["neighborhood"])))
            print(f"{count}: {room}")
            rooms.append(room)
            count += 1
            if count == LENGTH:
                break
    return rooms


async def fill_reservations():
    clients = await fill_clients()
    rooms = await fill_rooms()

    for i in range(LENGTH):
        random.seed(i + LENGTH + 456)
        print(i)
        client = clients[i]
        payload_post_client = {
            "name": client.name,
            "email": client.email
        }
        response_post = requests.post("http://localhost:80/clients/", json=payload_post_client)
        assert response_post.status_code == 200
        response_put_data = response_post.json()
        client_id = response_put_data["client_id"]
        print(f"{response_put_data}")

        room = rooms[i]
        payload_post_room = {
            "full_address": room.full_address,
            "description": room.description,
            "attributes": room.attributes
        }
        response_room = requests.post("http://localhost:80/rooms/", json=payload_post_room)
        response_put_room_data = response_room.json()
        room_id = response_put_room_data["room_id"]

        payload_post_reservation = {
            "client_id": client_id,
            "room_id": room_id,
            "start_booking_date": "2023-10-23T00:00:00",
            "end_booking_date": "2023-10-27T00:00:00",
            "booking_status": "unpaid"
        }
        response_reservation = requests.post("http://localhost:80/reservations/", json=payload_post_reservation)
        response_post_reservation_data = response_reservation.json()
        reservation_id = response_post_reservation_data["reservation_id"]
        print(f"{client_id} - {room_id} - {reservation_id}")
        print("------------------------------------------------------------------------------")

asyncio.run(fill_reservations())

