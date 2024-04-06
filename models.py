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





