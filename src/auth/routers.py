from fastapi import APIRouter, HTTPException,Response
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
async def register(data: UserCreate,response: Response):
    if not re.match(r"^\+7\d{10}$", data.number):
        raise HTTPException(
            status_code=400,
            detail="Номер телефона должен начинаться с +7 и содержать 10 цифр после него."
        )
    
    existing_user = await UsersServices.get_user_by_number(data.number)
    if existing_user:
        raise HTTPException(status_code=400, detail="Данный номер уже зарегистрирован")
    
    if (len(data.password) < 8 or
        not re.search(r"[A-Za-z]", data.password) or
        not re.search(r"[0-9]", data.password)):
        raise HTTPException (status_code=401,detail="Пароль должен быть не менее 8 сиволов содержать одну цифру и буквы разного регистра Z и z")
    
    
    ex_user = await UsersServices.get_user_by_email(data.email)
    if ex_user:
        raise HTTPException(status_code=400, detail="Данный Email уже зарегистрирован")
    
    hash_password = pwd_context.hash(data.password)
    new_data = data.dict()
    new_data["hashed_password"] = hash_password
    new_data["role"] = "user"
    
    new_user_id = await UsersServices.create_user(new_data)
    
    access_token = await AuthServices.create_access_token(user_id=new_user_id,role = new_data["role"])
    refresh_token = await AuthServices.create_refresh_token(user_id=new_user_id,role = new_data["role"])
    
    access_token_from_db = await AuthServices.save_access_token(access_token, user_id=new_user_id)
    refresh_token_from_redis = await AuthServices.save_refresh_tokens_to_redis(refresh_token, user_id=new_user_id)
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  
        secure=True,    
        samesite="lax", 
        max_age=3600    
        )


    return {"User": data.number, "message": "Регистрация прошла успешно"}




@router.post("/auth")
async def auth(data: UserLogin, response: Response):
    if not re.match(r"^\+7\d{10}$", data.number):
        raise HTTPException(
            status_code=400,
            detail="Номер телефона должен начинаться с +7 и содержать 10 цифр после него."
        )
    existing_user = await UsersServices.get_user_by_number(data.number)
    if existing_user is None:
        raise HTTPException(status_code=400, detail="Пользователь с таким номером телефона не найден,пройдите регистрацию")
    
    if not pwd_context.verify(data.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    
    access_token = await AuthServices.create_access_token(user_id = existing_user.id,role = existing_user.role)
    access_token = await AuthServices.save_access_token(access_token,user_id = existing_user.id)

    refresh_token = await AuthServices.verify_refresh_token(user_id = existing_user.id,role = existing_user.role)
    if refresh_token is None:
        refresh_token = await AuthServices.create_refresh_token(user_id = existing_user.id,role = existing_user.role)
        await AuthServices.save_refresh_tokens_to_redis(refresh_token,user_id= existing_user.id)
        return "Refresh токен успешно сохранен..."
        

    response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,  
            secure=True,    
            samesite="lax", 
            max_age=3600    
            )
    
    return {"User": data.number, "message": "Авторизация прошла успешно"}