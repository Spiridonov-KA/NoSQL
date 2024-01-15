from fastapi import APIRouter, HTTPException
from pymemcache import HashClient

from app.cache.memcached_utils import get_memcached_client
from app.client.repository_elasticsearch import *
from app.client.repository_mongo import *

client_router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}},
)


@client_router.get(
    "/"
)
async def get_all_client(mongo_repository: ClientMongoRepository = Depends(ClientMongoRepository.mongo_client_factory))\
        -> list[ClientSchema]:
    return await mongo_repository.get_all()


@client_router.get(
    "/{client_id}",
    response_description="Found client profile"
)
async def client_by_id(client_id: str,
                       mongo_repository: ClientMongoRepository = Depends(ClientMongoRepository.mongo_client_factory),
                       memcached_hash_client: HashClient = Depends(get_memcached_client)):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail='Bad Request')
    
    client = memcached_hash_client.get(client_id)
    if client is not None:
        return {"client": client}

    if (client := await mongo_repository.get_client(str(client_id))) is not None:
        return {"client": client}
    
    memcached_hash_client.add(client_id, client)
    raise HTTPException(status_code=404, detail=f'Client with ID : {client_id} not found')


@client_router.post(
    "/",
    response_description="Created client ID"
)
async def client_add(client_instance: UpdateClientSchema,
                     es_repository: ClientEsRepository = Depends(ClientEsRepository.es_client_factory),
                     mongo_repository: ClientMongoRepository = Depends(ClientMongoRepository.mongo_client_factory)):
    if (client_id := await mongo_repository.add_client(client_instance)) is not None:
        await es_repository.create(client_id, client_instance)
        return {"client_id": client_id}
    
    raise HTTPException(status_code=404, detail="Client already exists")


@client_router.put(
    "/{client_id}",
    response_description="Updated client"
)
async def client_update(client_id: str,
                        client_upd: UpdateClientSchema,
                        es_repository: ClientEsRepository = Depends(ClientEsRepository.es_client_factory),
                        mongo_repository: ClientMongoRepository = Depends(ClientMongoRepository.mongo_client_factory)):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail='Bad Request')

    if (updated_client := await mongo_repository.update_client(str(client_id), client_upd)) is not None:
        await es_repository.update(str(client_id), client_upd)
        return {"updated_client": updated_client}
    
    raise HTTPException(status_code=404, detail=f'Client with ID : {client_id} not found')


@client_router.delete(
    "/{client_id}",
    response_description="Deleted client id"
)
async def delete_client(client_id: str,
                        es_repository: ClientEsRepository = Depends(ClientEsRepository.es_client_factory),
                        mongo_repository: ClientMongoRepository = Depends(ClientMongoRepository.mongo_client_factory)):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail='Bad Request')

    if (deleted_client := await mongo_repository.delete_client(str(client_id))) is not None:
        await es_repository.delete(str(client_id))
        return {"client_id": deleted_client}
    
    raise HTTPException(status_code=404, detail=f'Client with ID : {client_id} not found')
