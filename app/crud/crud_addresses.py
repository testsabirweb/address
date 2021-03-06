from typing import List, Optional
from flask import jsonify

from databases import Database
from sqlalchemy.sql import select

from ..database import Address, addresses_table
from ..schemas import AddressSchema, ReturnAddress
import re

from math import cos, asin, sqrt, pi


def distance(lat1, lon1, lat2, lon2):
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * \
        cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 12742 * asin(sqrt(a))  # 2*R*asin...


regex_latitude = "^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$"
regex_longitude = "^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$"


async def create(database: Database, address: AddressSchema, user_id: int) -> int:

    if not re.fullmatch(regex_latitude, str(address.latitude)):
        return{
            "error": "invalid latitude"
        }

    if not re.fullmatch(regex_longitude, str(address.longitude)):
        return{
            "error": "invalid longitude"
        }

    query = addresses_table.insert().values(
        **address.dict(),
        writer_id=user_id
    )
    address_id: int = await database.execute(query)
    return address_id


async def read_all(database: Database, user_id: int) -> List[ReturnAddress]:
    query = addresses_table.select().where(
        addresses_table.c.writer_id == user_id
    )
    addresses_list: List[Address] = await database.fetch_all(query)
    return [ReturnAddress(**address) for address in addresses_list]


async def get_closest(database: Database, address: AddressSchema, user_id: int) -> ReturnAddress:
    query = addresses_table.select().where(
        addresses_table.c.writer_id == user_id
    )
    addresses_list: List[Address] = await database.fetch_all(query)
    result = False
    minDistance = float('inf')
    for add in addresses_list:
        dist = distance(address.latitude, address.longitude,
                        add.latitude, add.longitude)
        if dist < minDistance:
            minDistance = dist
            result = add

    return result


async def read_by_id(database: Database, address_id: int) -> None:
    query = addresses_table.select().where(
        addresses_table.c.id == address_id
    )
    address: Address = await database.fetch_one(query)
    return ReturnAddress(**address)


async def update(
        database: Database, address_id: int, updated_address: AddressSchema) -> None:
    query = addresses_table.update().values(
        **updated_address.dict()
    ).where(
        addresses_table.c.id == address_id
    )
    await database.execute(query)


async def delete(database: Database, address_id: int) -> None:
    query = addresses_table.delete().where(addresses_table.c.id == address_id)
    await database.execute(query)


async def get_writer_id(database: Database, address_id: int) -> Optional[int]:
    query = select([
        addresses_table.c.writer_id
    ]).where(
        addresses_table.c.id == address_id
    )
    address = await database.fetch_one(query)

    if address is not None:
        return address.writer_id
