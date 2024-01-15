import os
from fastapi import Depends
from datetime import datetime

from elasticsearch import AsyncElasticsearch

from app.repository.elasticsearch_utils import get_elasticsearch_client
from app.reservation.model import ReservationSchema, UpdateReservationSchema, BookStatusEnum


class ReservationEsRepository:
    _elasticsearch_client: AsyncElasticsearch
    _elasticsearch_index: str

    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        self._elasticsearch_client = elasticsearch_client
        self._elasticsearch_index = index

    @staticmethod
    def es_reservation_factory(elasticsearch_client: AsyncElasticsearch = Depends(get_elasticsearch_client)):
        elasticsearch_index = os.getenv('ELASTICSEARCH_INDEX_RESERVATION')
        return ReservationEsRepository(elasticsearch_index, elasticsearch_client)

    async def create(self, reservation_id: str, reservation: UpdateReservationSchema):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=reservation_id,
                                                document=dict(reservation))

    async def update(self, reservation_id: str, reservation: UpdateReservationSchema):
        await self._elasticsearch_client.update(index=self._elasticsearch_index, id=reservation_id,
                                                doc=dict(reservation))

    async def delete(self, reservation_id: str):
        await self._elasticsearch_client.delete(index=self._elasticsearch_index, id=reservation_id)

    async def find_by_client_id(self, client_id: str) -> list:
        name_query = {
            "match": {
                "client_id": client_id
            }
        }
        reservations = await self.find_by_query(name_query)
        return reservations

    async def find_by_booking_date(self, booking_date: datetime) -> list:
        booking_date_query = {
            "match": {
                "booking_date": booking_date
            }
        }
        reservations = await self.find_by_query(booking_date_query)
        return reservations

    async def find_by_range(self, left_date: datetime, right_date: datetime) -> list:
        range_date_query = {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "start_booking_date": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    },
                    {
                        "range": {
                            "end_booking_date": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    },
                ]
            }
        }
        reservations = await self.find_by_query(range_date_query)
        return reservations


    async def find_intersection(self, room_id: str, left_date: datetime, right_date: datetime) -> int:
        later_date_query = {
            "bool": {
                "filter": [
                    {"match": {"room_id": room_id}},
                    {"match": {"booking_status": BookStatusEnum.paid}},
                    {
                        "range": {
                            "start_booking_date": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    }
                ]
            }
        }
        later_reservations = await self.find_by_query(later_date_query)

        if len(later_reservations) != 0:
            return len(later_reservations)

        earlier_date_query = {
            "bool": {
                "filter": [
                    {"match": {"room_id": room_id}},
                    {"match": {"booking_status": BookStatusEnum.paid}},
                    {
                        "range": {
                            "end_booking_date": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    }
                ]
            }
        }
        earlier_reservations = await self.find_by_query(earlier_date_query)
        return len(earlier_reservations)

    async def find_upd_intersection(self, reservation_id: str,
                                    room_id: str, left_date: datetime, right_date: datetime) -> int:
        later_date_query = {
            "bool": {
                "must": [
                    {"match": {"room_id": room_id}},
                    {
                        "range": {
                            "start_booking_date": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    }
                ],
                "must_not": {
                    {"match": {"reservation_id": reservation_id}}
                }
            }
        }
        later_reservations = await self.find_by_query(later_date_query)

        if len(later_reservations) != 0:
            return len(later_reservations)

        earlier_date_query = {
            "bool": {
                "must": [
                    {"match": {"room_id": room_id}},
                    {
                        "range": {
                            "end_booking_date": {
                                "gte": left_date,
                                "lte": right_date,
                            }
                        }
                    }
                ],
                "must_not": {
                    {"match": {"reservation_id": reservation_id}}
                }
            }
        }
        earlier_reservations = await self.find_by_query(earlier_date_query)
        return len(earlier_reservations)

    async def find_by_room_id(self, room_id: str) -> list:
        booking_date_query = {
            "match": {
                "room_id": room_id
            }
        }
        reservations = await self.find_by_query(booking_date_query)
        return reservations

    async def find_by_query(self, query) -> list:
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query,
                                                           filter_path=['hits.hits._id', 'hits.hits._source'])
        if 'hits' not in response.body:
            return []
        result = response.body['hits']['hits']
        reservations = list(map(lambda reservation:
                                ReservationSchema(id=reservation['_id'],
                                                  client_id=reservation['_source']['client_id'],
                                                  room_id=reservation['_source']['room_id'],
                                                  start_booking_date=reservation['_source']['start_booking_date'],
                                                  end_booking_date=reservation['_source']['end_booking_date'],
                                                  booking_status=reservation['_source']['booking_status']), result))
        return reservations
