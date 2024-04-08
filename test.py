from models import *
import pandas as pd
import requests
import logging
import re


API_URL = "https://apidata.mos.ru/v1/"
API_KEY = "273c54c8-1509-4f9c-9923-e9050442285e"


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_response(url: str, flag_apikey: bool = False):
    api_key_str = "?api_key=" if flag_apikey == True else "&api_key="
    url = url + api_key_str + API_KEY    
    response = requests.get(url)
    if response.status_code == 200:    
        return response.json()        
    else:
        logging.error(f'Ошибка: {response.status_code}')


def get_department_affiliation_id(DepartamentalAffiliation: str):
    with db:
        query = DepartmentAffiliations.select(fn.COUNT(DepartmentAffiliations.id)).where(DepartmentAffiliations.name == DepartamentalAffiliation)
        count = query.scalar()
        # id = DepartmentAffiliations.select().where(DepartmentAffiliations.name == DepartamentalAffiliation)
        if count == 0:
            DepartmentAffiliations.insert({DepartmentAffiliations.name: DepartamentalAffiliation}).execute()
        
        id = DepartmentAffiliations.select().where(DepartmentAffiliations.name == DepartamentalAffiliation)
        return id[0]


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
        db.create_tables([AdmAreas, DistrictTypes, Districts, DepartmentAffiliations,
                          BikeParking, DogParks, DogParkPhotos, DogParkWorkingHours,
                          DogParkElements, DogParkIdElement, SportHalls,
                          SportHallWinterDimensions, SportHallPhotos, 
                          SportHallWorkingHours])
        logging.info("stone.db: tables created")
        query = [
            {"name": "район"},
            {"name": "поселение"},
            {"name": "городской округ"}
        ]
        DistrictTypes.insert_many(query).execute()
        logging.info("district_types table filled")


if __name__ == "__main__":
    # create_db()
    # scraping_wiki()
    skip = 0    
    data_count = get_response("https://apidata.mos.ru/v1/datasets/916/count", True)
    print(data_count)
    count = 0
    while True:        
        data = get_response("https://apidata.mos.ru/v1/datasets/916/rows?$top=500&$skip=" + str(skip))
        query = []
        for i in range(len(data)):
            # AdmArea = data[i]['Cells']['AdmArea']
            
            # if AdmArea.lower() == "зеленоградский административный округ":
            #     AdmArea_short = "ЗелАО"
            # else:
            #     AdmArea_short = ''.join(word[0].upper() for word in re.split(r'[ -]', AdmArea))                
            # id = AdmAreas.select().where(AdmAreas.name == AdmArea_short)
            # print(AdmArea, ": ", AdmArea_short, " id: ", id[0])
            
            # print(data[i]['Cells']['District'], ": ", re.sub(r'^\s*["\s]*(.*?)[\s"]*\s*$', r'\1', re.sub(r'^(городское поселение|район|поселение) | (городское поселение|район|поселение)$', '', data[i]['Cells']['District'])))
            
            # dep = data[i]['Cells']['DepartamentalAffiliation']
            # dep = "NULL" if data[i]['Cells']['Lighting'] not in ("да", "нет") else data[i]['Cells']['Lighting']
            # dep = data[i]['Cells']['Fencing'] == "да"
            # dep = data[i]['Cells']['geoData']['coordinates'][0]
            count += 1
            print(count, "-", data[i]['global_id'], ": ", type(data[i]['Cells']['ObjectOperOrgPhone']), len(data[i]['Cells']['ObjectOperOrgPhone']))
            # print(dep, ": ", id, ": ", id[0])
            # print(dep, ": ", get_department_affiliation_id(dep))



            # query.append(
            #     {
            #         "global_id": data[i]['Cells'].global_id,
            #         "admarea_id": get_adm_area_id(data[i]['Cells'].AdmArea),
            #         "district_id": get_district_id(data[i]['Cells'].District),
            #         "department_affiliation_id": get_department_affiliation_id(data[i]['Cells'].DepartamentalAffiliation),
            #         "address": data[i]['Cells'].Location.replace("Российская Федерация, город Москва, внутригородская территория", ""),
            #         "dog_park_area": data[i]['Cells'].DogParkArea,
            #         "lighting": True if data[i]['Cells'].Lighting == "да" else False,
            #         "fencing": True if data[i]['Cells'].Fencing == "да" else False,
            #         "longitude": data[i]['Cells']['geodata']['coordinates'][0],
            #         "latitude": data[i]['Cells']['geodata']['coordinates'][1]
            #     }
            # )
            # get_dog_park_photos(data[i]['Cells'].Photo)
            # get_elements(data[i]['Cells'].Elements)
        if len(data) < 500:
            break
        skip += 500

