import ormar
from typing import List, Optional
import databases
import pydantic
import sqlalchemy
from fastapi_users import models
from fastapi_users.db import OrmarBaseUserModel

metadata = sqlalchemy.MetaData()
database_ormar = databases.Database("sqlite:///test-ormar.db")
engine = sqlalchemy.create_engine("sqlite:///test-ormar.db")

class BaseMeta(ormar.ModelMeta):
    metadata = metadata 
    database = database_ormar

class User(models.BaseUser):
    sid: int = ormar.Integer(primary_key=True)
    fname: str = ormar.String(max_length=100)
    lname: str = ormar.String(max_length=100)


class UserCreate(models.BaseUserCreate):
    sid: int = ormar.Integer(primary_key=True)
    fname: str = ormar.String(max_length=100)
    lname: str = ormar.String(max_length=100)


class UserUpdate(User, models.BaseUserUpdate):
    sid: int = ormar.Integer(primary_key=True)
    fname: str = ormar.String(max_length=100)
    lname: str = ormar.String(max_length=100)


class UserDB(User, models.BaseUserDB):
    sid: int = ormar.Integer(primary_key=True)
    fname: str = ormar.String(max_length=100)
    lname: str = ormar.String(max_length=100)


class UserModel(OrmarBaseUserModel):
    class Meta(BaseMeta):
        tablename:str = "users"
    
    sid: int = ormar.Integer()
    fname: str = ormar.String(max_length=100)
    lname: str = ormar.String(max_length=100)


class Application(ormar.Model):
    class Meta(BaseMeta):
        tablename:str = "application"

    application_id: int = ormar.Integer(primary_key=True, auto_increment=True)
    sid: int = ormar.Integer()
    reg_number: str = ormar.String(max_length=12, unique=True)

    #boolean variables
    is_approved: bool = ormar.Boolean(default=False)
    is_car: bool = ormar.Boolean(default=False)
    is_bike: bool = ormar.Boolean(default=False)

    
    #image file names (files stored in an static/images/{img_type} folders with these names, for easier access)
    img_user_photo: str = ormar.String(max_length=100, default="")
    img_sid_name: str = ormar.String(max_length=100, default="")
    img_licence_name: str = ormar.String(max_length=100, default="")
    img_rc_name: str = ormar.String(max_length=100, default="")


class ApplicationRequest(pydantic.BaseModel):
    class Config:
        orm_mode = True

    reg_number:str
    is_car: bool 
    is_bike: bool

    