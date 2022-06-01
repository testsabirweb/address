from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .setup import Base

# Base models:


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String, nullable=False)

    addresses = relationship('Address', back_populates='writer')


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=True, default=0.0)
    longitude = Column(Float, nullable=True, default=0.0)

    writer_id = Column(Integer, ForeignKey('users.id'))
    writer = relationship('User', back_populates='addresses')


# Table objects:

users_table = User.__table__
addresses_table = Address.__table__
