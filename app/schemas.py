from typing import List

from pydantic import BaseModel


class AddressSchema(BaseModel):
    latitude: float = 0.0
    longitude: float = 0.0


class ReturnAddress(AddressSchema):
    id: int = None


class AddressesListSchema(BaseModel):
    addresses: List[ReturnAddress]


class UserSchema(BaseModel):
    id: int = None
    username: str
    password: str
