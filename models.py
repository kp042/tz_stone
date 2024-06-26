from peewee import *


db = SqliteDatabase("stone.db")


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = "id"


class AdmAreas(BaseModel):
    name = CharField()

    class Meta:
        db_table = "adm_areas"


class DistrictTypes(BaseModel):
    name = CharField()

    class Meta:
        db_table = "district_types"


class Districts(BaseModel):
    name = CharField()
    district_type_id = ForeignKeyField(DistrictTypes)
    admarea_id = ForeignKeyField(AdmAreas)

    class Meta:
        db_table = "districts"


class DepartmentAffiliations(BaseModel):
    name = CharField()

    class Meta:
        db_table = "department_affiliations"


class BikeParking(BaseModel):
    global_id = IntegerField()
    name = CharField()
    photo = CharField()
    admarea_id = ForeignKeyField(AdmAreas)
    district_id = ForeignKeyField(Districts)
    department_affiliation_id = ForeignKeyField(DepartmentAffiliations)
    address = CharField()
    capacity = IntegerField()
    object_oper_org_name = CharField()
    object_oper_org_phone = CharField()    
    longitude = DecimalField(max_digits=11, decimal_places=9)
    latitude = DecimalField(max_digits=12, decimal_places=9)

    class Meta:
        db_table = "bike_parking"


class DogParks(BaseModel):
    global_id = IntegerField()    
    admarea_id = ForeignKeyField(AdmAreas)
    district_id = ForeignKeyField(Districts)
    department_affiliation_id = ForeignKeyField(DepartmentAffiliations)
    location = CharField()
    dog_park_area = FloatField()
    lighting = BooleanField()
    fencing = BooleanField()
    longitude = DecimalField(max_digits=11, decimal_places=9)
    latitude = DecimalField(max_digits=12, decimal_places=9)

    class Meta:
        db_table = "dog_parks"


class DogParkPhotos(BaseModel):
    dog_park_id = ForeignKeyField(DogParks)
    photo = CharField()

    class Meta:
        db_table = "dog_park_photos"


class DogParkWorkingHours(BaseModel):
    dog_park_id = ForeignKeyField(DogParks)
    monday = CharField()
    tuesday = CharField()
    wednesday = CharField()
    thursday = CharField()
    friday = CharField()
    saturday = CharField()
    sunday = CharField()

    class Meta:
        db_table = "dog_park_working_hours"


class DogParkElements(BaseModel):
    name = CharField()

    class Meta:
        db_table = "dog_park_elements"


class DogParkIdElement(BaseModel):
    dog_park_id = ForeignKeyField(DogParks)
    dog_park_element_id = ForeignKeyField(DogParkElements)

    class Meta:
        db_table = "dog_park_id_element"



class SportHalls(BaseModel):
    global_id = IntegerField()
    name = CharField()
    name_winter = CharField()
    photo_winter = CharField()
    admarea_id = ForeignKeyField(AdmAreas)
    district_id = ForeignKeyField(Districts)    
    address = CharField()
    email = CharField()    
    help_phone = CharField()    
    has_equipment_rental = BooleanField()
    equipment_rental_comments = CharField()
    has_tech_service = BooleanField()
    tech_serv_comments = CharField()
    has_dressing_room = BooleanField()
    has_eatery = BooleanField()
    has_toilet = BooleanField()
    has_wifi = BooleanField()
    has_cash_machine = BooleanField()
    has_first_aid_post = BooleanField()
    has_music = BooleanField()
    usage_period_winter = CharField()
    lighting = CharField()
    surface_type_winter = CharField()
    seats = IntegerField()
    paid = BooleanField()
    paid_comments = CharField()
    disability_friendly = CharField()
    service_winter = CharField()
    longitude = DecimalField(max_digits=11, decimal_places=9)
    latitude = DecimalField(max_digits=12, decimal_places=9)    

    class Meta:
        db_table = "sport_halls"


class SportHallWinterDimensions(BaseModel):
    sport_hall_id = ForeignKeyField(SportHalls)
    square = FloatField()
    length = FloatField()
    width = FloatField()
    
    class Meta:
        db_table = "sport_hall_winter_dimensions"


class SportHallWebsites(BaseModel):
    sport_hall_id = ForeignKeyField(SportHalls)
    website = CharField()
    negotiability = BooleanField()

    class Meta:
        db_table = "sport_hall_websites"


class SportHallWorkingHours(BaseModel):
    sport_hall_id = ForeignKeyField(SportHalls)
    monday = CharField()
    tuesday = CharField()
    wednesday = CharField()
    thursday = CharField()
    friday = CharField()
    saturday = CharField()
    sunday = CharField()

    class Meta:
        db_table = "sport_hall_working_hours"
