from models import *
import pandas as pd
import requests
import logging
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

API_URL = "https://apidata.mos.ru/v1/"
API_KEY = "273c54c8-1509-4f9c-9923-e9050442285e"
DATASETS = [916, 60622, 2663]


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_response(url: str):
    url = url + "&api_key=" + API_KEY
    response = requests.get(url)
    if response.status_code == 200:    
        return response.json()        
    else:
        logging.error(f'Ошибка: {response.status_code}')


def get_sport_halls():
    pass


def get_dogs_parks():
    pass


def get_bike_parking():
    pass


def scraping_wiki():
    wiki_url = "https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B_%D0%B8_%D0%BF%D0%BE%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%8B"
    tables = pd.read_html(wiki_url)    
    admareas_df = tables[0].iloc[:,4:6]
    admareas_df.columns = ["district", "adm_area"]
    admareas_set = sorted(set(admareas_df.adm_area))
    query1 = [{'name': x} for x in admareas_set]
    with db:
        AdmAreas.insert_many(query1).execute()
        logging.info("adm_areas table filled")
        query2 = []
        for _, row in admareas_df.iterrows():
            id = AdmAreas.select().where(AdmAreas.name == row.adm_area)
            if row.district.find("поселение") != -1:
                query2.append({"name": row.district.replace(", поселение", ""),
                            "district_type_id": 2,
                            "admarea_id": id[0]})
            elif row.district.find("городской округ") != -1:
                query2.append({"name": row.district.replace(", городской округ", ""),
                            "district_type_id": 3,
                            "admarea_id": id[0]})
            else:
                query2.append({"name": row.district,
                            "district_type_id": 1,
                            "admarea_id": id[0]})        
        Districts.insert_many(query2).execute()
        logging.info("districts table filled")


def create_db():
    with db:
        db.create_tables([AdmAreas, DistrictTypes, Districts])
        logging.info("stone.db: tables created")
        query = [
            {"name": "район"},
            {"name": "поселение"},
            {"name": "городской округ"}
        ]
        DistrictTypes.insert_many(query).execute()
        logging.info("district_types table filled")


if __name__ == "__main__":    
    create_db()
    scraping_wiki()
    # with db:
    #     results = AdmAreas.select().where(AdmAreas.name == "СВАО")
    #     print(results[0])
        # for result in results:
        #     print(result.id)


