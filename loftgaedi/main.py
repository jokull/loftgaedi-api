from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .scrape import scrape

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = get_user(user_id=user_id, db=db)
    return crud.update_user(db=db, db_user=db_user, user=user)


@app.get("/", response_model=List[schemas.Station])
def get_stations(db: Session = Depends(get_db)):
    return crud.get_stations(db=db)


@app.get("/scrape")
def get_scrape(db: Session = Depends(get_db)):
    scraped = []
    for name, status in scrape(db):
        scraped.append([name, status])
    return {"scraped": scraped}
