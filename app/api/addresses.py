from urllib import response
from fastapi import APIRouter, Depends, HTTPException

from ..crud import crud_addresses
from ..deps import Database, get_current_user, get_db
from ..schemas import AddressSchema, AddressesListSchema, UserSchema

router = APIRouter()


@router.get('/addresses', response_model=AddressesListSchema)
async def list_all(
    user: UserSchema = Depends(get_current_user),
    database: Database = Depends(get_db)
):
    addresses_list = await crud_addresses.read_all(database, user.id)
    return {'addresses': addresses_list}


@router.get('/addresses/{address_id}', response_model=AddressSchema)
async def get_by_id(
    address_id: int,
    user: UserSchema = Depends(get_current_user),
    database: Database = Depends(get_db)
):
    writer_id = await crud_addresses.get_writer_id(database, address_id)

    if not writer_id:
        raise HTTPException(404)

    if writer_id != user.id:
        raise HTTPException(403, detail='Couldn\'t edit. Wrong Authorization.')

    address = await crud_addresses.read_by_id(database, address_id)
    return address


@router.post('/addresses', status_code=201)
async def create(
    address: AddressSchema,
    user: UserSchema = Depends(get_current_user),
    database: Database = Depends(get_db)
):
    address_id = await crud_addresses.create(database, address, user.id)
    return {'id': address_id}


@router.delete('/addresses/{address_id}', status_code=204)
async def delete(
    address_id: int,
    user: UserSchema = Depends(get_current_user),
    database: Database = Depends(get_db)
):
    writer_id = await crud_addresses.get_writer_id(database, address_id)

    if not writer_id:
        raise HTTPException(404)

    if writer_id != user.id:
        raise HTTPException(
            403, detail='Couldn\'t delete. Wrong Authorization.')

    await crud_addresses.delete(database, address_id)


@router.put('/addresses/{address_id}', status_code=204)
async def edit(
    address_id: int,
    updated_address: AddressSchema,
    user: UserSchema = Depends(get_current_user),
    database: Database = Depends(get_db)
):
    writer_id = await crud_addresses.get_writer_id(database, address_id)

    if not writer_id:
        raise HTTPException(404)

    if writer_id != user.id:
        raise HTTPException(403, detail='Couldn\'t edit. Wrong Authorization.')

    await crud_addresses.update(database, address_id, updated_address)


@router.post('/addresses/close', response_model=AddressSchema)
async def get_by_location(
    address: AddressSchema,
    user: UserSchema = Depends(get_current_user),
    database: Database = Depends(get_db)
):
    address = await crud_addresses.get_closest(database, address, user.id)

    if not address:
        raise HTTPException(404, detail='Couldn\'t find closest location.')

    return address
