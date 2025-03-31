from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from src.categories.schemas import New_category
from src.admin.services import Admin_services
from src.categories.models import Category
from src.users.schemas import UserSeach
from src.database import async_session_maker
from src.users.models import User
from src.auth.services import AuthServices
from sqlalchemy.orm import selectinload
from src.categories.schemas import find_category_by_id
router = APIRouter()


# ___________________Права для пользователей_______________________________________________________________________________________________________________________________________________________________________________________________

@router.patch("/Privileges add Admin")
async def add_admin_user(data: UserSeach,request: Request):
    role = await Admin_services.get_role_from_cookie(request)
    if role != "admin":
        raise HTTPException(status_code= 404, detail= "У вас не достаточно прав для использования!")
    async with async_session_maker() as session:
        # Поиск пользователя по номеру
        query = select(User).where(User.number == data.number)
        result = await session.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем роль пользователя
        user.role = "admin"

        await session.refresh(user)
        access_token = await AuthServices.create_access_token(user.id,user.role)
        await AuthServices.save_access_token(access_token,user.id)
        refresh_token = AuthServices.create_refresh_token(user.id,user.role)
        await AuthServices.save_refresh_tokens_to_redis(refresh_token,user.id)
        # Сохраняем изменения в базе данных
        await session.commit()
        

        return {"message": "Вы выдали пользователю права Администратора"}


@router.patch("/Privileges off")
async def delete_privileges_user(data: UserSeach,request: Request):
    role = await Admin_services.get_role_from_cookie(request)
    if role != "admin":
        raise HTTPException(status_code= 404, detail= "У вас не достаточно прав для использования!")
    
    async with async_session_maker() as session:
        # Поиск пользователя по номеру
        query = select(User).where(User.number == data.number)
        result = await session.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем роль пользователя
        user.role = "user"

        await session.refresh(user)

        access_token = await AuthServices.create_access_token(user.id,user.role)
        await AuthServices.save_access_token(access_token,user.id)
        refresh_token = AuthServices.create_refresh_token(user.id,user.role)
        await AuthServices.save_refresh_tokens_to_redis(refresh_token,user.id)
        # Сохраняем изменения в базе данных
        await session.commit()
        

        return {"message": "Вы забрали у пользователя права Администратора"}    
    
@router.patch("/Privileges worker")
async def add_worker_user(data: UserSeach,request: Request):
    role = await Admin_services.get_role_from_cookie(request)
    if role != "admin":
        raise HTTPException(status_code= 404, detail= "У вас не достаточно прав для использования!")
    async with async_session_maker() as session:
        # Поиск пользователя по номеру
        query = select(User).where(User.number == data.number)
        result = await session.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем роль пользователя
        user.role = "worker"
        # Меняем токены пользователю чтобыы снести роль сразу а не через час
        await session.refresh(user)
        
        access_token = await AuthServices.create_access_token(user.id,user.role)
        await AuthServices.save_access_token(access_token,user.id)
        refresh_token = AuthServices.create_refresh_token(user.id,user.role)
        await AuthServices.save_refresh_tokens_to_redis(refresh_token,user.id)
        # Сохраняем изменения в базе данных
        await session.commit()
        

        return {"message": "Вы выдали пользователю права Рабочий"}  

# ___________________Категории_______________________________________________________________________________________________________________________________________________________________________________________________

@router.post("/Add category")
async def add_new_categori(data:New_category):
    new_data = data.dict()
    new_category_id = await Admin_services.create_new_category(new_data)    
    return f"Категория с именем {data.name} успешно создана!"




@router.delete("/delete category")
async def delete_categories(data:find_category_by_id):
    async with async_session_maker() as session:
        result = await session.execute(
            select(Category)
            .options(selectinload(Category.children))  
            .filter(Category.id == data.id))  
        category = result.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        for child in category.children:
            await session.delete(child)
        # Удаляем главную категорию
        await session.delete(category)
        await session.commit()
        return "Категория  удалена , с ней же удалились все ее зависимые категории"


# ___________________Продукты_______________________________________________________________________________________________________________________________________________________________________________________________