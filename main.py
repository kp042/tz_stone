from models import *
import pandas as pd
import requests
import logging
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


API_KEY = ""

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def scraping_wiki():
    wiki_url = "https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B_%D0%B8_%D0%BF%D0%BE%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%8B"
    tables = pd.read_html(wiki_url)    
    admareas_df = tables[0].iloc[:,4:6]
    admareas_df.columns = ["district", "adm_area"]
    admareas_set = sorted(set(admareas_df.adm_area))
    query1 = [{'name': x} for x in admareas_set]
    with db:
        AdmAreas.insert_many(query1).execute()
        logging.info("administration areas added to adm_areas table")
    query2 = []
    for district in list(admareas_df.district):
        pass


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
        logging.info("district types created")


if __name__ == "__main__":    
    create_db()
    scraping_wiki()    

