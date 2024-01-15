import os
from fastapi import Depends

from elasticsearch import AsyncElasticsearch

from app.repository.elasticsearch_utils import get_elasticsearch_client
from app.room.model import RoomSchema, UpdateRoomSchema, Address


class RoomEsRepository:
    _elasticsearch_client: AsyncElasticsearch
    _elasticsearch_index: str

    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        self._elasticsearch_client = elasticsearch_client
        self._elasticsearch_index = index

    @staticmethod
    def es_room_factory(elasticsearch_room: AsyncElasticsearch = Depends(get_elasticsearch_client)):
        elasticsearch_index = os.getenv('ELASTICSEARCH_INDEX_ROOM')
        return RoomEsRepository(elasticsearch_index, elasticsearch_room)

    async def create(self, room_id: str, room: UpdateRoomSchema):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=room_id,
                                                document=dict(room))

    async def update(self, room_id: str, room: UpdateRoomSchema):
        await self._elasticsearch_client.update(index=self._elasticsearch_index, id=room_id,
                                                doc=dict(room))

    async def delete(self, room_id: str):
        await self._elasticsearch_client.delete(index=self._elasticsearch_index, id=room_id)

    async def find_by_attribute(self, attribute: str):
        attributes_query = {
            "bool": {
                "must": [
                    {"match_phrase": {"attributes": attribute}},
                ]
            }
        }
        rooms = await self.find_by_query(attributes_query)
        return rooms

    async def find_by_country(self, country_name: str):
        country_name_query = {
            "bool": {
                "must": [
                    {"match": {"full_address.country": country_name}},
                ]
            }
        }
        rooms = await self.find_by_query(country_name_query)
        return rooms

    async def find_by_city(self, city_name: str):
        city_name_query = {
            "bool": {
                "must": [
                    {"match": {"full_address.city": city_name}},
                ]
            }
        }
        rooms = await self.find_by_query(city_name_query)
        return rooms

    async def find_by_query(self, filter_query) -> list:
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=filter_query,
                                                           filter_path=['hits.hits._id', 'hits.hits._source'])
        if 'hits' not in response.body:
            return []
        result = response.body['hits']['hits']
        rooms = list(map(lambda room:
                         RoomSchema(id=room['_id'],
                                    description=room['_source']['description'],
                                    attributes=room['_source']['attributes'],
                                    full_address=Address(
                                        country=room['_source']['full_address']['country'],
                                        city=room['_source']['full_address']['city'],
                                        address=room['_source']['full_address']['address']
                                    )), result))
        return rooms