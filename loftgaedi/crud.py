from sqlalchemy.orm import Session

from . import models, schemas


def get_stations(db: Session):
    return db.query(models.Station).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).get(user_id)


def update_user(db: Session, db_user: models.User, user: schemas.UserUpdate):
    if user.notify:
        db_user.notify = user.notify
    if user.location_id is not None:
        db_user.location_id = user.location_id
    db.add(db_user)
    db.commit()
    return db_user
