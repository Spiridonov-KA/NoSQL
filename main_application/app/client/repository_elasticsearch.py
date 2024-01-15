import os
from fastapi import Depends

from elasticsearch import AsyncElasticsearch

from app.repository.elasticsearch_utils import get_elasticsearch_client
from app.client.model import ClientSchema, UpdateClientSchema


class ClientEsRepository:
    # Клиент для эластика
    _elasticsearch_client: AsyncElasticsearch
    _elasticsearch_index: str

    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        self._elasticsearch_client = elasticsearch_client
        self._elasticsearch_index = index

    @staticmethod
    def es_client_factory(elasticsearch_client: AsyncElasticsearch = Depends(get_elasticsearch_client)):
        elasticsearch_index = os.getenv('ELASTICSEARCH_INDEX_CLIENT')
        return ClientEsRepository(elasticsearch_index, elasticsearch_client)

    async def create(self, client_id: str, client: UpdateClientSchema):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=client_id, document=dict(client))

    async def update(self, client_id: str, client: UpdateClientSchema):
        await self._elasticsearch_client.update(index=self._elasticsearch_index, id=client_id, doc=dict(client))

    async def delete(self, client_id: str):
        await self._elasticsearch_client.delete(index=self._elasticsearch_index, id=client_id)
