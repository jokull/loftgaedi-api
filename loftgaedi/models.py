from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    comment = Column(String)
    status = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    active = Column(Boolean, default=True)
    measurements = Column(JSONB, default={})
    last_measurement = Column(DateTime, nullable=True)
    last_scrape = Column(DateTime, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, server_default=func.now())

    # Null station indicates the user does not want notifications
    station_id = Column(Integer, ForeignKey(Station.id), nullable=True)
    station = relationship(Station)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)
    station_id = Column(Integer, ForeignKey(Station.id))
    station = relationship(Station)
