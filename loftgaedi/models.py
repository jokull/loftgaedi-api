import decimal

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .database import Base

measurement_thresholds = {
    "h2s": (
        "25.0000000",
        "50.0000000",
        "75.0000000",
        "100.0000000",
    ),
    "pm10": (
        "25.0000000",
        "50.0000000",
        "75.0000000",
        "100.0000000",
    ),
    "pm1": (
        "10.0000000",
        "15.0000000",
        "25.0000000",
        "50.0000000",
    ),
    "pm25": (
        "10.0000000",
        "15.0000000",
        "25.0000000",
        "50.0000000",
    ),
    "no2": (
        "50.0000000",
        "75.0000000",
        "150.0000000",
        "200.0000000",
    ),
    "so2": (
        "50.0000000",
        "100.0000000",
        "200.0000000",
        "350.0000000",
    ),
    "co": (
        "0.5000000",
        "1.0000000",
        "2.5000000",
        "5.0000000",
    )
}


def get_stat_status(key, value):
    value = decimal.Decimal(value)
    thresholds = measurement_thresholds.get(key)
    if thresholds is None:
        return
    value = decimal.Decimal(value)
    for threshold_status, threshold in enumerate(map(decimal.Decimal, thresholds), 2):
        if value > threshold:
            return threshold_status
    return 1


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

    @property
    def stats(self):
        _stats = []
        for key, value in (self.measurements or {}).items():
            status = None
            if value is not None:
                status = get_stat_status(key, value) or None
            _stats.append({'key': key, 'value': value, 'status': status})
        return _stats


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
