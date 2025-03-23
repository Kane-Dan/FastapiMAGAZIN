from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from authlib.jose import jwt as jwt_authlib
import jwt
from fastapi import HTTPException
from sqlalchemy import select
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY,REDIS_URL
from src.database import async_session_maker
from src.users.services import UsersServices
from passlib.context import CryptContext
from src.auth.models import Tokens
from src.users.schemas import UserLogin
from src.auth.models import Tokens
from jwt import ExpiredSignatureError
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthServices:
    # Создание временого токена
    async def create_access_token(user_id: int):
        payload = {
            "sub": user_id,  # user_id как число
            "exp": datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return access_token
        
    # сохранение временого токена
    async def save_access_token(token: str, user_id: int):
        async with async_session_maker() as session:
            existing_token: Tokens = await session.execute(
                select(Tokens).where(Tokens.user_id == user_id)
            )
            existing_token = existing_token.scalars().first()
            if existing_token:
                existing_token.token = token
                existing_token.expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                await session.commit()
                return existing_token.token
            else:
                new_token: Tokens = Tokens(
                    token=token,
                    expires_at=datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
                    user_id=user_id,
                )
                session.add(new_token)
                await session.commit()
                return new_token.token
    
    # верификация временого токена
    async def verify_access_token(data: dict):        
        token = data.get("token")
        user_id = data.get("user_id")
        if not token or not user_id:
            raise HTTPException(status_code=400, detail="Неверные данные: отсутствует token или user_id")
        async with async_session_maker() as session:
            async with session.begin():
                
                result = await session.execute(
                    select(Tokens).where(Tokens.user_id == user_id, Tokens.token == token)
                )
                token_entry = result.scalars().first()

                if not token_entry:
                    raise HTTPException(status_code=401, detail="Токен не найден")
            
                if token_entry.expires_at < datetime.utcnow():
                    
                    refresh_token = await AuthServices.verify_refresh_token(user_id)

                    
                    new_access_token = await AuthServices.create_access_token(user_id)  # Используем await

                    # Обновляем токен в базе данных
                    token_entry.token = new_access_token
                    token_entry.expires_at = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

                    # Сохраняем изменения
                    session.add(token_entry)
                    await session.commit()

                    print("Новый токен создан и сохранен.")
                    return new_access_token

                print("Токен не истек, возвращаем существующий токен.")
                return token_entry.token
            
    # получение временого токена
    async def get_access_token(user_id: int) -> str:
        async with async_session_maker() as session:
            async with session.begin():
            
                result = await session.execute(
                select(Tokens).where(Tokens.user_id == user_id)
                )
                token_entry = result.scalars().first()

                if token_entry:
                    return token_entry.token  # Возвращаем токен для верификации
                else:
                    return None 
    
    # Создание токена обновления
    async def create_refresh_token(user_id: int):
        payload = {
        "sub": user_id,  
        "exp": datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    }
        refresh_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return refresh_token
    
    # Сохранение токена обновления
    async def save_refresh_tokens_to_redis(refresh_token,user_id,refresh_ttl=int(REFRESH_TOKEN_EXPIRE_DAYS)):
        await REDIS_URL.set(f"refresh_token:{user_id}", refresh_token, ex=refresh_ttl * 86400)
        token = await AuthServices.get_refresh_token(user_id)
        return token
        


    # Получчение токена обновления
    async def get_refresh_token(user_id: int):
        refresh_token = await REDIS_URL.get(f"refresh_token:{user_id}")
        if refresh_token is None:
            print(f"No token found for user ID {user_id}")
            return None
        return refresh_token.decode("utf-8")
    
    
    # Верефикация токена обновления
    async def verify_refresh_token(user_id: int):
        stored_refresh_token = await REDIS_URL.get(f"refresh_token:{user_id}")
        
        if stored_refresh_token is None:
            raise HTTPException(status_code=404, detail="Токен не найден")

        refresh_token = stored_refresh_token.decode('utf-8')
        print(refresh_token)
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            await REDIS_URL.delete(f"refresh_token:{user_id}")
            raise HTTPException(status_code=401, detail="Токен истек и был удален")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Неправильный токен")
        return refresh_token
