import requests
import datetime as dt

STATIONS_URL = "https://loftgaedi.is/search?filter%5Btype%5D=INDICATOR"
STATION_CSV_URL = "https://loftgaedi.is/station/csv?filter%5BstationId%5D={station_id}"

name_split_characters = ".;"


dialect = {
    "header": True,
    "skipBlankRows": True,
    "delimiter": ";",
    "encoding": "utf-8-sig",
}

csv_headers = {
    "Dagsetning": None,
    "PM10": "pm10",
    "NO2": "no2",
    "SO2": "so2",
    "H2S": "h2s",
    "CO": "co",
    "PM1": "pm1",
    "PM2.5": "pm25",
    "Raki": "humidity",
    "Loftþr.": "pressure",
    "Vindhr.": "wind",
    "Vindhr.max": "wind_max",
    "Vindátt": "vector",
    "Hiti": "temperature",
}


color_status_map = {
    "#3ab734": 1,  # Mjög gott
    "#80c75e": 2,  # Gott
    "#efef33": 3,  # Miðlungs
    "#e2791b": 4,  # Slæmt
    "#f13838": 5,  # Mjög slæmt
}


def parse_stats(stats):
    for stat in stats:
        if not stat:
            yield None
        else:
            yield stat.replace(",", ".")


def parse_date(date_string):
    date, time = date_string.strip('"').split(" ")
    date, time = date.split("-"), time.split(":")
    return dt.datetime(*(int(s) for s in (date + time)))


def get_station_intervals(station_id):
    response = requests.get(STATION_CSV_URL.format(station_id=station_id))
    response.encoding = "utf-8-sig"

    headers, *lines = [
        line for line in response.text.splitlines() if line
    ]  # clean empty lines
    headers = [
        csv_headers[h] for h in headers.split(";")[1:]
    ]  # `1:` because first column is date

    for line in lines:
        date_string, *stats = line.split(";")
        yield parse_date(date_string), dict(zip(headers, parse_stats(stats)))


def get_clean_station_data(station_data):
    name, comment = station_data["name"], None
    for character in name_split_characters:
        if character in name:
            name, comment = name.split(character, 1)
    name, comment = name.strip(), comment.strip() if comment else comment
    return {
        "id": station_data["id"],
        "name": name.strip(" "),
        "comment": comment,
        "status": color_status_map[station_data["colorCode"]],
        "latitude": station_data["lat"],
        "longitude": station_data["lon"],
    }


def get_stations():
    response = requests.get(
        STATIONS_URL, headers={"X-Requested-With": "XMLHttpRequest"}
    )
    map_data = response.json()["mapData"]
    for station_data in map_data:
        yield get_clean_station_data(station_data)


def main():

    from loftgaedi.models import Station, Base
    from loftgaedi.database import SessionLocal, engine

    db = SessionLocal()
    Base.metadata.create_all(bind=engine)

    try:
        for station in get_stations():
            print(station["name"], station["status"])
            db_station = db.query(Station).get(station["id"])
            if db_station is None:
                db_station = Station(**station)
            else:
                db_station.status = station["status"]
            for date, measurements in get_station_intervals(station["id"]):
                db_station.measurements = measurements
                db_station.last_measurements = date
                db_station.last_scrape = dt.datetime.utcnow()
                break
            db.add(db_station)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    from ipdb import launch_ipdb_on_exception

    with launch_ipdb_on_exception():
        main()
