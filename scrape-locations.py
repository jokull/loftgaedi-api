from loftgaedi.scrape import scrape
from loftgaedi.database import SessionLocal


if __name__ == "__main__":
    db = SessionLocal()
    try:
        for name, status in scrape(db):
            print(name, status)
    finally:
        db.close()
