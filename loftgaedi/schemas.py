from typing import Dict, Optional, List
from pydantic import BaseModel


class Stat(BaseModel):
    key: str
    value: str = None
    status: int = None

    class Config:
        orm_mode = True


class StationBase(BaseModel):
    name: str
    comment: str = None
    status: int
    longitude: str
    latitude: str


class Station(StationBase):
    id: int
    measurements: Dict[str, Optional[str]]
    stats: List[Stat]

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
