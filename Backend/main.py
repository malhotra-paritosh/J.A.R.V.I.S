from typing import List, Optional
from ormar.exceptions import *
from ormar_models import database_ormar, engine, metadata
from ormar_models import Application
from ormar_models import User, UserCreate, UserUpdate, UserDB, UserModel, ApplicationRequest
from fastapi_users import FastAPIUsers
from fastapi_users.db import OrmarUserDatabase
from fastapi_users.authentication import JWTAuthentication
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status

#routers
from routers import application_routes

#user_db is a reference to the user table for fastapi-users
metadata.create_all(engine)
user_db = OrmarUserDatabase(UserDB, UserModel)

#fastapi-users stuff, jwt auth
SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
jwt_authentication = JWTAuthentication(secret=SECRET, lifetime_seconds=3600, tokenUrl="auth/jwt/login")

app = FastAPI()
app.state.database = database_ormar
fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
current_active_user = fastapi_users.current_user(active=True)

app.include_router(fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(SECRET), prefix="/auth", tags=["auth"],)
app.include_router(fastapi_users.get_verify_router(SECRET),prefix="/auth",tags=["auth"],)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])
app.include_router(application_routes.router)

@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()

@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()





@app.post("/application/docs_upload/")
async def upload_documents(reg_num: str, sid_img: UploadFile = File(...), licence_img:UploadFile = File(...),rc_img: UploadFile = File(...), user:User = Depends(current_active_user)):
    
    user_sid = user.sid

    ext_sid_file = sid_img.filename.split(".")[-1] 
    if ext_sid_file not in ["jpg", "jpeg", "png"]:
        return {"msg":"Image must be jpg or png format"}

    ext_licence_file = licence_img.filename.split(".")[-1] 
    if ext_licence_file not in ["jpg", "jpeg", "png"]:
        return {"msg":"Image must be jpg or png format"}
    
    ext_rc_file = rc_img.filename.split(".")[-1] 
    if ext_rc_file not in ["jpg", "jpeg", "png"]:
        return {"msg":"Image must be jpg or png format"}

    sid_img_filename = f"{user_sid}_img_sid.{ext_sid_file}"
    licence_img_filename = f"{user_sid}_img_licence.{ext_licence_file}"
    rc_img_filename = f"{user_sid}_img_rc.{ext_rc_file}"

    with open(f"static/image/sid_card/{sid_img_filename}", "wb+") as f:
        f.write(sid_img.file.read())
    
    with open(f"static/image/licence/{licence_img_filename}", "wb+") as f:
        f.write(licence_img.file.read())

    with open(f"static/image/rc/{rc_img_filename}", "wb+") as f:
        f.write(rc_img.file.read())

    application = await Application.objects.get(reg_number = reg_num)

    application.img_sid_name = sid_img_filename
    application.img_licence_name = licence_img_filename
    application.img_rc_name = rc_img_filename

    application.update()
    return{'msg':'documents uploaded successfully'}


@app.post("/application/photo_upload/")
async def upload_user_photo(reg_num: str, user_photo: UploadFile = File(...), user:User = Depends(current_active_user)):
 
    user_sid = user.sid

    ext_user_photo = user_photo.filename.split(".")[-1] 
    if ext_user_photo not in ["jpg", "jpeg", "png"]:
        return {"msg":"Image must be jpg or png format"}

    photo_img_filename = f"{user_sid}_img_photo.{ext_user_photo}"

    with open(f"static/image/user/{photo_img_filename}", "wb+") as f:
        f.write(user_photo.file.read())

    application = await Application.objects.get(reg_number = reg_num)

    application.img_user_photo = photo_img_filename
    await application.update()
    return{'msg':'user photo uploaded successfully'}


'''
@app.get("/items/", response_model=List[Item])
async def get_items():
    items = await Item.objects.select_related("category").all()
    return items


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    await item.save()
    return item


@app.post("/categories/", response_model=Category)
async def create_category(category: Category):
    await category.save()
    return category


@app.put("/items/{item_id}")
async def get_item(item_id: int, item: Item):
    item_db = await Item.objects.get(pk=item_id)
    return await item_db.update(**item.dict())


@app.delete("/items/{item_id}")
async def delete_item(item_id: int, item: Item = None):
    if item:
        return {"deleted_rows": await item.delete()}
    item_db = await Item.objects.get(pk=item_id)
    return {"deleted_rows": await item_db.delete()}
'''

if __name__ == "__main__":
    # to play with API run the script and visit http://127.0.0.1:8000/docs
    uvicorn.run(app, host="127.0.0.1", port=8000)