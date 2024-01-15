import requests

BASE_ENDPOINT_ROOMS = "http://localhost:8000/rooms"


def test_can_call_endpoint_rooms():
    response = requests.get(BASE_ENDPOINT_ROOMS)
    assert response.status_code == 200


def test_get_room():
    payload_post_room = {
        "full_address":
        {
            "country": "Test_Country_get_yyyy",
            "city": "Test_City_get_yyyy",
            "address": "Test_Address_get_yyyy"
        },
        "description": "Test_desc_getyyy",
        "attributes": "att1 att2 att3 att4 get5 yyyy",
        "booking_status": True
    }
    response_post = requests.post(BASE_ENDPOINT_ROOMS + "/", json=payload_post_room)
    assert response_post.status_code == 200
    response_put_data = response_post.json()
    room_id = response_put_data["room_id"]

    response_get = requests.get(BASE_ENDPOINT_ROOMS + f"/{room_id}/")
    assert response_get.status_code == 200
    response_get_data = response_get.json()
    assert response_get_data["room"]["description"] == payload_post_room["description"]
    assert response_get_data["room"]["attributes"] == payload_post_room["attributes"]
    assert response_get_data["room"]["booking_status"] == payload_post_room["booking_status"]
    assert response_get_data["room"]["full_address"]["country"] == payload_post_room["full_address"]["country"]
    assert response_get_data["room"]["full_address"]["city"] == payload_post_room["full_address"]["city"]
    assert response_get_data["room"]["full_address"]["address"] == payload_post_room["full_address"]["address"]


def test_put_room():
    payload_post_room = {
        "full_address":
        {
            "country": "Test_Country_putty",
            "city": "Test_City_putty",
            "address": "Test_Address_putty"
        },
        "description": "Test_desc_putty",
        "attributes": "att1 att2 att3 att4 put5",
        "booking_status": True
    }
    response_post = requests.post(BASE_ENDPOINT_ROOMS + "/", json=payload_post_room)
    assert response_post.status_code == 200
    response_post_data = response_post.json()
    room_id = response_post_data["room_id"]

    payload_put = {
        "full_address":
        {
            "country": "Test_Country_put_",
            "city": "Test_City_put_",
            "address": "Test_Address_put_"
        },
        "description": "Test_desc_put_tttttttttttt",
        "attributes": "att1 att2 att3 att4 put5_",
        "booking_status": False
    }
    response_put = requests.put(BASE_ENDPOINT_ROOMS + f"/{room_id}/", json=payload_put)
    assert response_put.status_code == 200

    response_get = requests.get(BASE_ENDPOINT_ROOMS + f"/{room_id}/")
    assert response_get.status_code == 200
    response_get_data = response_get.json()
    assert response_get_data["room"]["description"] == payload_put["description"]
    assert response_get_data["room"]["attributes"] == payload_put["attributes"]
    assert response_get_data["room"]["booking_status"] == payload_put["booking_status"]
    assert response_get_data["room"]["full_address"]["country"] == payload_put["full_address"]["country"]
    assert response_get_data["room"]["full_address"]["city"] == payload_put["full_address"]["city"]
    assert response_get_data["room"]["full_address"]["address"] == payload_put["full_address"]["address"]
