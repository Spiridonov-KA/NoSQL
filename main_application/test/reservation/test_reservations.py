import requests

BASE_ENDPOINT_RESERVATIONS = "http://localhost:8000/reservations"
BASE_ENDPOINT_CLIENTS = "http://localhost:8000/clients"
BASE_ENDPOINT_ROOMS = "http://localhost:8000/rooms"


def test_can_call_endpoint_clients():
    response = requests.get(BASE_ENDPOINT_RESERVATIONS)
    assert response.status_code == 200


def test_post_reservations():
    payload_post_client = {
        "name": "reserve_test_client_aa",
        "email": "reserve_test_client_aa@gmail.com"
    }
    response_post_client = requests.post(BASE_ENDPOINT_CLIENTS + "/", json=payload_post_client)
    assert response_post_client.status_code == 200
    response_put_client_data = response_post_client.json()
    client_id = response_put_client_data["client_id"]

    payload_post_room = {
        "full_address":
        {
            "country": "Test_Country_get_reserveaa",
            "city": "Test_City_get_reserveaa",
            "address": "Test_Address_get_reserveaa"
        },
        "description": "Test_desc_get_reserveaa",
        "attributes": "att1 att2 att3 res4 get5",
        "booking_status": True
    }
    response_post_room = requests.post(BASE_ENDPOINT_ROOMS + "/", json=payload_post_room)
    assert response_post_room.status_code == 200
    response_put_room_data = response_post_room.json()
    room_id = response_put_room_data["room_id"]

    payload_post_reservation = {
        "client_id": client_id,
        "room_id": room_id,
        "booking_date": "2022-10-23T00:00:00",
        "booking_status": "unpaid"
    }
    response_post_reservation = requests.post(BASE_ENDPOINT_RESERVATIONS + "/", json=payload_post_reservation)
    assert response_post_reservation.status_code == 200
    response_post_reservation_data = response_post_reservation.json()
    reservation_id = response_post_reservation_data["reservation_id"]

    response_get_reservation = requests.get(BASE_ENDPOINT_RESERVATIONS + f"/{reservation_id}/")
    assert response_get_reservation.status_code == 200
    response_get_data = response_get_reservation.json()
    assert response_get_data["reservation"]["client_id"] == client_id
    assert response_get_data["reservation"]["room_id"] == room_id
    assert response_get_data["reservation"]["booking_date"] == payload_post_reservation["booking_date"]
    assert response_get_data["reservation"]["booking_status"] == payload_post_reservation["booking_status"]

    payload_put_reservation = {
        "client_id": client_id,
        "room_id": room_id,
        "booking_date": "2022-10-23T00:00:00",
        "booking_status": "paid"
    }
    response_put_reservation = requests.put(BASE_ENDPOINT_RESERVATIONS + f"/{reservation_id}/", json=payload_put_reservation)
    assert response_put_reservation.status_code == 200
    response_put_reservation_data = response_put_reservation.json()
    reservation_id = response_put_reservation_data["updated_reservation"]["id"]

    response_get_reservation = requests.get(BASE_ENDPOINT_RESERVATIONS + f"/{reservation_id}/")
    assert response_get_reservation.status_code == 200
    response_get_data = response_get_reservation.json()
    assert response_get_data["reservation"]["client_id"] == client_id
    assert response_get_data["reservation"]["room_id"] == room_id
    assert response_get_data["reservation"]["booking_date"] == payload_put_reservation["booking_date"]
    assert response_get_data["reservation"]["booking_status"] == payload_put_reservation["booking_status"]
