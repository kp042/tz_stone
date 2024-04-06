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


# class DataInfo(BaseModel):
#     name = CharField()
   

class DepartmentAffiliations(BaseModel):
    name = CharField()

    class Meta:
        db_table = "department_affiliations"


class BikeParking(BaseModel):
    name = CharField()    
    # photo = CharField()  - photos
    admarea_id = ForeignKeyField(AdmAreas)
    district_id = ForeignKeyField(Districts)
    department_affiliation_id = ForeignKeyField()
    address = CharField()
    capacity = IntegerField()
    object_oper_org_id = ForeignKeyField()
    longitude = DecimalField(max_digits=10, decimal_places=8)
    latitude = DecimalField(max_digits=11, decimal_places=8)

    class Meta:
        db_table = "bike_parking"


class DogParks(BaseModel):
    name = CharField()
    # photos
    admarea_id = ForeignKeyField(AdmAreas)
    district_id = ForeignKeyField(Districts)
    department_affiliation_id = ForeignKeyField()
    address = CharField()
    dog_park_area = IntegerField()
    lighting = BooleanField()
    fencing = BooleanField()
    longitude = DecimalField(max_digits=10, decimal_places=8)
    latitude = DecimalField(max_digits=11, decimal_places=8)

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
    name = CharField()
    department_affiliation_id = ForeignKeyField()
    photo = CharField()



    class Meta:
        db_table = "sport_halls"


class SportHallWorkingHours(BaseModel):
    sport_hall_id = ForeignKeyField(SportHalls)
    monday = CharField()
    tuesday = CharField()
    wednesday = CharField()
    thursday = CharField()
    friday = CharField()
    saturday = CharField()
    sunday = CharField()
