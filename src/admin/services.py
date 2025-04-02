from fastapi import HTTPException, Request
import jwt
from sqlalchemy import select
from src.config import ALGORITHM, SECRET_KEY
from src.database import async_session_maker
from src.users.models import User
from fastapi.responses import JSONResponse
from src.categories.models import Category
from src.categories.schemas import New_category
from src.products.models import Product

class Admin_services:       
    async def get_role_from_cookie(request: Request):
        access_token = request.cookies.get("access_token")

        # Проверяем наличие токена и его формат
        if not access_token or not access_token.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"message": "Authentication required for paths containing '/admin'."},
            )

        # Извлекаем токен
        token = access_token.split(" ")[1]  
        try:
            # Декодируем токен
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_role = payload.get("role")

            # Проверяем роль пользователя
            if user_role != "admin":
                return JSONResponse(
                    status_code=403,
                    content={"message": "Access denied. Admin role required."},
                )

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"message": "Token has expired."},
            )
        except jwt.PyJWTError:
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid token."},
            )

        
        return user_role  


    async def create_new_category(data: dict):
        async with async_session_maker() as session:
            parent_name = data.get("parent_name", None)
            parent_category = None  

            # Проверяем, указан ли родитель
            if parent_name:
                result = await session.execute(select(Category).where(Category.name == parent_name))
                parent_category = result.scalars().first()
                if not parent_category:
                    raise HTTPException(status_code=404, detail="Parent category not found")

            # Создаем новую категорию
            new_category = Category(
                name=data["name"],
                parent_name=parent_name  # Здесь parent_name может быть None
            )

            session.add(new_category)
            await session.commit()
            await session.refresh(new_category)

            return new_category.id

    async def get_category_by_name(Category_name):
        async with async_session_maker() as session:
            result = await session.execute(select(Category).where(Category.name == Category_name))    
            category = result.scalars().first()
            return category




        
    async def create_new_product(data:dict):
        async with async_session_maker() as session:
            product_category_name = data.get("category_name")

            result = await Admin_services.get_category_by_name(Category_name = product_category_name  )
              
            if not result:
                raise HTTPException(status_code= 404,detail="Категория с таким именнем не найдена!")

            new_product = Product(
                name = data["name"],
                price = data["price"],
                picture = data["picture"],
                description = data["description"],
                category_id = result.id
            )                                
            session.add(new_product)
            await session.commit()
            await session.refresh(new_product)
            return new_product.id
        
    
