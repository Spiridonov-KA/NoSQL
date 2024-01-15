import requests

BASE_ENDPOINT_CLIENTS = "http://localhost:80/clients"


def test_can_call_endpoint_clients():
    response = requests.get(BASE_ENDPOINT_CLIENTS)
    assert response.status_code == 200


def test_get_client():
    payload_post_client = {
        "name": "test_client_1",
        "email": "test_client_1@gmail.com"
    }
    response_post = requests.post(BASE_ENDPOINT_CLIENTS + "/", json=payload_post_client)
    assert response_post.status_code == 200
    response_put_data = response_post.json()
    print(f"{response_put_data}")
    client_id = response_put_data["client_id"]

    response_get = requests.get(BASE_ENDPOINT_CLIENTS + f"/{client_id}/")
    assert response_get.status_code == 200
    response_get_data = response_get.json()
    assert response_get_data["client"]["name"] == payload_post_client["name"]
    assert response_get_data["client"]["email"] == payload_post_client["email"]


def test_put_client():
    payload_post_client = {
        "name": "test_client_another",
        "email": "test_client_another@gmail.com"
    }
    response_post = requests.post(BASE_ENDPOINT_CLIENTS + "/", json=payload_post_client)
    assert response_post.status_code == 200
    response_put_data = response_post.json()
    client_id = response_put_data["client_id"]

    payload_put_client = {
        "name": "test_client_another_put",
        "email": "test_client_another_put@gmail.com"
    }
    response_put = requests.put(BASE_ENDPOINT_CLIENTS + f"/{client_id}/", json=payload_put_client)
    assert response_put.status_code == 200

    response_get = requests.get(BASE_ENDPOINT_CLIENTS + f"/{client_id}/")
    assert response_get.status_code == 200
    response_get_data = response_get.json()
    assert response_get_data["client"]["name"] == payload_put_client["name"]
    assert response_get_data["client"]["email"] == payload_put_client["email"]


def test_delete_client():
    payload_post_client = {
        "name": "test_client_delete__",
        "email": "test_client_delete___@gmail.com"
    }
    response_post = requests.post(BASE_ENDPOINT_CLIENTS + "/", json=payload_post_client)
    assert response_post.status_code == 200
    response_post_data = response_post.json()
    client_id = response_post_data["client_id"]

    response_delete = requests.delete(BASE_ENDPOINT_CLIENTS + f"/{client_id}/")
    assert response_delete.status_code == 200
