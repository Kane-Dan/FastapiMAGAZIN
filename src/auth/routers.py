from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
import redis
from src.auth.services import AuthServices
from src.users.services import UsersServices
from src.users.schemas import UserCreate,UserLogin
import re
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(data: UserCreate):
    if not re.match(r"^\+7\d{10}$", data.number):
        raise HTTPException(
            status_code=400,
            detail="Номер телефона должен начинаться с +7 и содержать 10 цифр после него."
        )
    
    existing_user = await UsersServices.get_user_by_number(data.number)
    if existing_user:
        raise HTTPException(status_code=400, detail="Данный номер уже зарегистрирован")
    
    ex_user = await UsersServices.get_user_by_email(data.email)
    if ex_user:
        raise HTTPException(status_code=400, detail="Данный Email уже зарегистрирован")
    
    hash_password = pwd_context.hash(data.password)
    new_data = data.dict()
    new_data["hashed_password"] = hash_password
    
    new_user_id = await UsersServices.create_user(new_data)
    
    access_token = await AuthServices.create_access_token(user_id=new_user_id)
    refresh_token = await AuthServices.create_refresh_token(user_id=new_user_id)
    
    access_token_from_db = await AuthServices.save_access_token(access_token, user_id=new_user_id)
    refresh_token_from_redis = await AuthServices.save_refresh_tokens_to_redis(refresh_token, user_id=new_user_id)
    
    return JSONResponse(
        status_code=200,
        content={"refresh_token": refresh_token_from_redis, "access_token": access_token_from_db}
    )



@router.post("/auth")
async def auth(data: UserLogin):
    existing_user = await UsersServices.get_user_by_number(data.number)
    
    if existing_user is None:
        raise HTTPException(status_code=400, detail="Пользователь с таким номером не найден")
    
    if not pwd_context.verify(data.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    
    refresh_token = await AuthServices.create_refresh_token(existing_user.id)
    
    refresh_token_from_redis = await AuthServices.save_refresh_tokens_to_redis(
        refresh_token, user_id=existing_user.id
    )

    access_token = await AuthServices.get_access_token(user_id=existing_user.id)
    
    if access_token is None:
        access_token = await AuthServices.create_access_token(existing_user.id)
        access_token_from_db = await AuthServices.save_access_token(access_token, user_id=existing_user.id)
        return {"access_token": access_token_from_db}
    
    access_token = await AuthServices.verify_access_token(
        data={"token": access_token, "user_id": existing_user.id}
    )
    return JSONResponse(
        status_code=200,
        content={"refresh_token": refresh_token_from_redis, "access_token": access_token}
    )



