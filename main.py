from models import *
import pandas as pd
import requests
import logging
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

API_URL = "https://apidata.mos.ru/v1/"
API_KEY = "273c54c8-1509-4f9c-9923-e9050442285e"
# DATASETS = {"bike": 916, "dogs": 2663, "sport": 60622}
WEEK_DAYS = {"понедельник": "monday",
             "вторник": "tuesday",
             "среда": "wednesday",
             "четверг": "thursday",
             "пятница": "friday",
             "суббота": "saturday",
             "воскресенье": "sunday"
             }

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


def get_adm_area_id(AdmArea: str):
    logging.info("get_adm_area_id")
    if AdmArea.lower() == "зеленоградский административный округ":
        AdmArea_short = "ЗелАО"
    else:
        AdmArea_short = ''.join(word[0].upper() for word in re.split(r'[ -]', AdmArea))
    with db:
        id = AdmAreas.select().where(AdmAreas.name == AdmArea_short)
    return id[0]


def get_district_id(District: str):
    logging.info("get_district_id")
    District = re.sub(r'^\s*["\s]*(.*?)[\s"]*\s*$', r'\1', re.sub(r'^(городское поселение|район|поселение) | (городское поселение|район|поселение)$', '', District))
    District = District.replace("ё", "е")
    logging.info(District)
    with db:
        id = Districts.select().where(Districts.name == District)
    return id[0]


def get_department_affiliation_id(DepartamentalAffiliation: str):
    logging.info("get_department_affiliation_id")
    with db:
        query = DepartmentAffiliations.select(fn.COUNT(DepartmentAffiliations.id)).where(DepartmentAffiliations.name == DepartamentalAffiliation)
        count = query.scalar()
        if count == 0:
            DepartmentAffiliations.insert({DepartmentAffiliations.name: DepartamentalAffiliation}).execute()
        
        id = DepartmentAffiliations.select().where(DepartmentAffiliations.name == DepartamentalAffiliation)
        return id[0]
    

def get_dog_park_photos(Photos: list, dog_park_id: int):
    logging.info("get_dog_park_photos")
    for photo in Photos:
        with db:
            DogParkPhotos.insert({DogParkPhotos.dog_park_id: dog_park_id,
                                  DogParkPhotos.photo: photo['Photo']}).execute()


def get_dog_park_elements(Elements: list, dog_park_id: int):
    logging.info("get_dog_park_elements")
    for element in Elements:
        with db:
            query = DogParkElements.select(fn.COUNT(DogParkElements.id)).where(DogParkElements.name == element)
            count = query.scalar()
            if count == 0:
                DogParkElements.insert({DogParkElements.name: element}).execute()
            
            id = DogParkElements.select().where(DogParkElements.name == element)
            DogParkIdElement.insert({DogParkIdElement.dog_park_id: dog_park_id,
                                     DogParkIdElement.dog_park_element_id: id[0]}).execute()


def get_dog_park_working_hours(WeekDays: list, dog_park_id: int):
    logging.info("get_dog_park_working_hours")
    with db:
        query = {DogParkWorkingHours.dog_park_id: dog_park_id,
                 DogParkWorkingHours.monday: WeekDays[0]['Hours'],
                 DogParkWorkingHours.tuesday: WeekDays[1]['Hours'],
                 DogParkWorkingHours.wednesday: WeekDays[2]['Hours'],
                 DogParkWorkingHours.thursday: WeekDays[3]['Hours'],
                 DogParkWorkingHours.friday: WeekDays[4]['Hours'],
                 DogParkWorkingHours.saturday: WeekDays[5]['Hours'],
                 DogParkWorkingHours.sunday: WeekDays[6]['Hours']}
        
        DogParkWorkingHours.insert(query).execute()


def get_dogs_parks():
    skip = 0 
    while True:
        data = get_response("https://apidata.mos.ru/v1/datasets/2663/rows?$top=500&$skip=" + str(skip))
        for i in range(len(data)):
            query = {
                    "global_id": data[i]['Cells']['global_id'],
                    "admarea_id": get_adm_area_id(data[i]['Cells']['AdmArea']),
                    "district_id": get_district_id(data[i]['Cells']['District']),
                    "department_affiliation_id": get_department_affiliation_id(data[i]['Cells']['DepartamentalAffiliation']),
                    "location": data[i]['Cells']['Location'],
                    "dog_park_area": data[i]['Cells']['DogParkArea'],
                    "lighting": data[i]['Cells']['Lighting'] == "да",
                    "fencing": data[i]['Cells']['Fencing'] == "да",
                    "longitude": data[i]['Cells']['geoData']['coordinates'][0],
                    "latitude": data[i]['Cells']['geoData']['coordinates'][1]
                    }
            with db:
                DogParks.insert(query).execute()
                dog_park_id = DogParks.select().where(DogParks.global_id == data[i]['Cells']['global_id'])[0]
            get_dog_park_photos(data[i]['Cells']['Photo'], dog_park_id)
            if isinstance(data[i]['Cells']['Elements'], str):
                Elements = []
                Elements.append(data[i]['Cells']['Elements'])
            else:
                Elements = data[i]['Cells']['Elements']
            get_dog_park_elements(Elements, dog_park_id)
            get_dog_park_working_hours(data[i]['Cells']['WorkingHours'], dog_park_id)
            logging.info(f"dog_park_id: {dog_park_id} done")
        if len(data) < 500:
            break
        skip += 500
    logging.info("dog parks data added")


def get_bike_parking():
    skip = 0
    while True:
        data = get_response("https://apidata.mos.ru/v1/datasets/916/rows?$top=500&$skip=" + str(skip))
        for i in range(len(data)):
            query = {
                    "global_id": data[i]['Cells']['global_id'],
                    "name": data[i]['Cells']['Name'],
                    "photo": data[i]['Cells']['Photo'],
                    "admarea_id": get_adm_area_id(data[i]['Cells']['AdmArea']),
                    "district_id": get_district_id(data[i]['Cells']['District']),
                    "department_affiliation_id": get_department_affiliation_id(data[i]['Cells']['DepartmentalAffiliation']),
                    "address": data[i]['Cells']['Address'],
                    "capacity": data[i]['Cells']['Capacity'],
                    "object_oper_org_name": "ГКУ Центр организации дорожного движения Правительства Москвы",
                    "object_oper_org_phone": "(495) 361-78-07",                    
                    "longitude": data[i]['Cells']['geoData']['coordinates'][0],
                    "latitude": data[i]['Cells']['geoData']['coordinates'][1]
                    }
            with db:
                BikeParking.insert(query).execute()
                bike_park_id = BikeParking.select().where(BikeParking.global_id == data[i]['Cells']['global_id'])[0]
                logging.info(f"bike_park_id: {bike_park_id} done")
        if len(data) < 500:
            break
        skip += 500
    logging.info("bike parks data added")


def get_sport_hall_working_hours(WeekDays: list, sport_hall_id: int):
    logging.info("get_sport_hall_working_hours")
    with db:
        query = {SportHallWorkingHours.sport_hall_id: sport_hall_id,
                 SportHallWorkingHours.monday: WeekDays[0]['Hours'],
                 SportHallWorkingHours.tuesday: WeekDays[1]['Hours'],
                 SportHallWorkingHours.wednesday: WeekDays[2]['Hours'],
                 SportHallWorkingHours.thursday: WeekDays[3]['Hours'],
                 SportHallWorkingHours.friday: WeekDays[4]['Hours'],
                 SportHallWorkingHours.saturday: WeekDays[5]['Hours'],
                 SportHallWorkingHours.sunday: WeekDays[6]['Hours']}        
        SportHallWorkingHours.insert(query).execute()


def get_sport_hall_dimensions_winter(Dimensions: dict, sport_hall_id: int):
    logging.info("get_sport_hall_dimensions_winter")
    with db:
        query = {SportHallWinterDimensions.sport_hall_id: sport_hall_id,
                 SportHallWinterDimensions.square: Dimensions['Square'],
                 SportHallWinterDimensions.length: Dimensions['Length'],
                 SportHallWinterDimensions.width: Dimensions['Width']}
        SportHallWinterDimensions.insert(query).execute()


def url_check(url: str):
    if "http://" not in url and "https://" not in url:
        try:
            response = requests.get("http://" + url)
            if response.status_code == 200:
                return True        
            response = requests.get("https://" + url)
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.RequestException as e:
            logging.info(f"url_check error: {e}")
            return False            
    elif "http://" in url or "https://" in url:
        try:
            r = requests.head(url)
            return r.status_code == 200
        except requests.exceptions.RequestException as e:
            return False


def get_sport_hall_website(website: str, sport_hall_id: int):
    if len(website) > 0 and website is not None:
        with db:
            query = {SportHallWebsites.sport_hall_id: sport_hall_id,
                 SportHallWebsites.website: website,
                 SportHallWebsites.negotiability: url_check(website)}
            SportHallWebsites.insert(query).execute()


def get_sport_halls():
    skip = 0
    while True:
        data = get_response("https://apidata.mos.ru/v1/datasets/60622/rows?$top=500&$skip=" + str(skip))
        for i in range(len(data)):
            logging.info(f"global_id: {data[i]['global_id']}")
            query = {
                    "global_id": data[i]['global_id'],
                    "name": data[i]['Cells']['ObjectName'],
                    "name_winter": data[i]['Cells']['NameWinter'],
                    "photo_winter": data[i]['Cells']['PhotoWinter'][0]['Photo'],
                    "admarea_id": get_adm_area_id(data[i]['Cells']['AdmArea']),
                    "district_id": get_district_id(data[i]['Cells']['District']),
                    "address": data[i]['Cells']['Address'],
                    "email": data[i]['Cells']['Email'],                    
                    "help_phone": data[i]['Cells']['HelpPhone'] if len(data[i]['Cells']['HelpPhone']) != 0 else "",
                    "has_equipment_rental": data[i]['Cells']['HasEquipmentRental'] == "да",
                    "equipment_rental_comments": data[i]['Cells']['EquipmentRentalComments'],
                    "has_tech_service": data[i]['Cells']['HasTechService'] == "да",
                    "tech_serv_comments": data[i]['Cells']['TechServiceComments'],
                    "has_dressing_room": data[i]['Cells']['HasDressingRoom'] == "да",
                    "has_eatery": data[i]['Cells']['HasEatery'] == "да",
                    "has_toilet": data[i]['Cells']['HasToilet'] == "да",
                    "has_wifi": data[i]['Cells']['HasWifi'] == "да",
                    "has_cash_machine": data[i]['Cells']['HasCashMachine'] == "да",
                    "has_first_aid_post": data[i]['Cells']['HasFirstAidPost'] == "да",
                    "has_music": data[i]['Cells']['HasMusic'] == "да",
                    "usage_period_winter": data[i]['Cells']['UsagePeriodWinter'],
                    "lighting": data[i]['Cells']['Lighting'],
                    "surface_type_winter": data[i]['Cells']['SurfaceTypeWinter'],
                    "seats": data[i]['Cells']['Seats'],
                    "paid": data[i]['Cells']['Paid'] == "платно",
                    "paid_comments": data[i]['Cells']['PaidComments'], 
                    "disability_friendly": "" if data[i]['Cells']['DisabilityFriendly'] is None else data[i]['Cells']['DisabilityFriendly'], 
                    "service_winter": data[i]['Cells']['ServicesWinter'],
                    "longitude": data[i]['Cells']['geoData']['coordinates'][0],
                    "latitude": data[i]['Cells']['geoData']['coordinates'][1]
                    }
            with db:
                SportHalls.insert(query).execute()
                sport_hall_id = SportHalls.select().where(SportHalls.global_id == data[i]['Cells']['global_id'])[0]
                logging.info(f"sport_hall_id: {sport_hall_id} done")
            get_sport_hall_website(data[i]['Cells']['WebSite'], sport_hall_id)
            get_sport_hall_working_hours(data[i]['Cells']['WorkingHoursWinter'], sport_hall_id)
            get_sport_hall_dimensions_winter(data[i]['Cells']['DimensionsWinter'][0], sport_hall_id)
        if len(data) < 500:
            break
        skip += 500
    logging.info("sport halls data added")


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
            district_name = row.district.replace("ё", "е")
            if row.district.find("поселение") != -1:
                query2.append({"name": district_name.replace(", поселение", ""),
                            "district_type_id": 2,
                            "admarea_id": id[0]})
            elif row.district.find("городской округ") != -1:
                query2.append({"name": district_name.replace(", городской округ", ""),
                            "district_type_id": 3,
                            "admarea_id": id[0]})
            else:
                query2.append({"name": district_name,
                            "district_type_id": 1,
                            "admarea_id": id[0]})
        Districts.insert_many(query2).execute()
        logging.info("districts table filled")


def create_db():
    with db:
        db.create_tables([AdmAreas, DistrictTypes, Districts, DepartmentAffiliations,
                          BikeParking, DogParks, DogParkPhotos, DogParkWorkingHours,
                          DogParkElements, DogParkIdElement, SportHalls, SportHallWebsites,
                          SportHallWinterDimensions, SportHallWorkingHours])
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
    get_dogs_parks()
    get_bike_parking()
    get_sport_halls()

