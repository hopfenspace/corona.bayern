#!/usr/bin/env python3
import json
from datetime import datetime

import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


def try_parsing_date(text):
    for fmt in ('Stand: %d.%m.%Y, %H:%M Uhr', 'Stand: %H:%M Uhr, %d.%m.%Y ', 'Stand: %H:%M Uhr, %d.%m.%Y'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    print(text)
    raise ValueError('no valid date format found')


def main():
    result = requests.get("https://coronamaps.de/covid-19-coronavirus-live-karte-bayern/")
    data = "".join([x for x in result.text.splitlines() if x.startswith("var mapsvg_options")][0].split("=")[1:]).split(
        ";jQuery")[0]
    data_json = json.loads(data)
    data_db = data_json["data_db"]["objects"]

    engine = create_engine(open("connectorstring").read(), echo=True)
    base = declarative_base()

    class Data(base):
        __tablename__ = 'data'

        id = Column(Integer, primary_key=True, autoincrement=True)
        infected = Column(Integer)
        deaths = Column(Integer)
        recovered = Column(Integer)
        date = Column(DateTime)
        source_1 = Column(String(200))
        source_2 = Column(String(200))
        location_id = Column(ForeignKey("Location.id"))
        location = relationship("Location", back_populates="data")

    class Location(base):
        __tablename__ = "location"
        id = Column(Integer, primary_key=True, autoincrement=True)
        title = Column(String(200), unique=True)
        locality = Column(String(200))
        administrative_area_level_3 = Column(String(200))
        administrative_area_level_3_short = Column(String(5))
        administrative_area_level_2 = Column(String(200))
        administrative_area_level_1 = Column(String(200))
        administrative_area_level_1_short = Column(String(5))
        country = Column(String(200))
        country_short = Column(String(5))
        lat = Column(Float)
        long = Column(Float)
        data = relationship("Data", back_populates="location")

    base.metadata.create_all(engine)
    session_builder = sessionmaker(bind=engine)
    session = session_builder()

    data_list = []

    for item in data_db:
        location = None if not item["location"] \
            else Location(locality=item["location"]["address"].get("locality"),
                          administrative_area_level_3=item["location"]["address"].get("administrative_area_level_3"),
                          administrative_area_level_3_short=item["location"]["address"].get(
                              "administrative_area_level_3_short"),
                          administrative_area_level_2=item["location"]["address"].get("administrative_area_level_2"),
                          administrative_area_level_1=item["location"]["address"].get("administrative_area_level_1"),
                          administrative_area_level_1_short=item["location"]["address"].get(
                              "administrative_area_level_1_short"),
                          country=item["location"]["address"]["country"],
                          country_short=item["location"]["address"]["country_short"],
                          lat=item["location"]["lat"],
                          long=item["location"]["lng"])
        d = Data(infected=int(item["infizierte"]) if item["infizierte"] != "" else 0,
                 deaths=int(item["todesfaelle"]) if item["todesfaelle"] != "" else 0,
                 recovered=int(item["geheilte"]) if item["geheilte"] != "" else 0,
                 date=try_parsing_date(item["datum"]),
                 source_1=item["quelle_1"], source_2=item["quelle_2"],
                 location=location)
        data_list.append(d)

    session.add_all(data_list)
    session.commit()


if __name__ == '__main__':
    main()
