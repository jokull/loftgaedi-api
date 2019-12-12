from typing import Dict, Optional
from pydantic import BaseModel


class StationBase(BaseModel):
    name: str
    comment: str = None
    status: int
    longitude: str
    latitude: str


class Station(StationBase):
    id: int
    measurements: Dict[str, Optional[str]]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    notify: bool = False


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    location_id: int = None
    notify: bool = None


class User(UserBase):
    id: int
    location: StationBase

    class Config:
        orm_mode = True
