#!/usr/bin/env python3
import json
from datetime import datetime

import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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

        id = Column(Integer, primary_key=True)
        infected = Column(Integer)
        deaths = Column(Integer)
        recovered = Column(Integer)
        date = Column(DateTime)
        source_1 = Column(String)
        source_2 = Column(String)
        political = Column(String, unique=True)
        locality = Column(String)
        administrative_area_level_3 = Column(String)
        administrative_area_level_3_short = Column(String)
        administrative_area_level_2 = Column(String)
        administrative_area_level_1 = Column(String)
        administrative_area_level_1_short = Column(String)
        country = Column(String)
        country_short = Column(String)
        lat = Column(Float)
        lng = Column(Float)

    base.metadata.create_all(engine)
    session_builder = sessionmaker(bind=engine)
    session = session_builder()

    data_list = []

    for item in data_db:
        d = Data(infected=int(item["infizierte"]) if item["infizierte"] != "" else 0,
                 deaths=int(item["todesfaelle"]) if item["todesfaelle"] != "" else 0,
                 recovered=int(item["geheilte"]) if item["geheilte"] != "" else 0,
                 date=try_parsing_date(item["datum"]),
                 source_1=item["quelle_1"], source_2=item["quelle_2"])
        if item["location"]:
            d.political = item["location"]["address"].get("political"),
            d.locality = item["location"]["address"].get("locality"),
            d.administrative_area_level_3 = item["location"]["address"].get("administrative_area_level_3"),
            d.administrative_area_level_3_short = item["location"]["address"].get(
                "administrative_area_level_3_short")
            d.administrative_area_level_2 = item["location"]["address"].get("administrative_area_level_2"),
            d.administrative_area_level_1 = item["location"]["address"].get("administrative_area_level_1"),
            d.administrative_area_level_1_short = item["location"]["address"].get(
                "administrative_area_level_1_short")
            d.country = item["location"]["address"]["country"]
            d.country_short = item["location"]["address"]["country_short"]
            d.lat = item["location"]["lat"]
            d.lng = item["location"]["lng"]
        data_list.append(d)

    session.add_all(data_list)
    session.commit()


if __name__ == '__main__':
    main()
