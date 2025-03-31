from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from src.database import async_session_maker 
from src.categories.models import Category
from sqlalchemy.orm import selectinload
from src.categories.schemas import find_category_by_id, find_category_by_name
router = APIRouter()


@router.get("/main_categories")
async def  get_all_main_categories():
    async with async_session_maker() as session:
        result = await session.execute(select(Category).filter(Category.parent_name.is_(None)))
        all_categories = result.scalars().all()

       
        return all_categories

    
@router.get("/categories")
async def  get_all_main_categories():
    async with async_session_maker() as session:
        result = await session.execute(
        select(Category)
        .options(selectinload(Category.children))  
        .filter(Category.parent_name.is_(None)))
        all_categories = result.scalars().all()

       
        return all_categories


@router.post("/subcategories/{category_id}") 
async def get_subcategories(data:find_category_by_id):
    async with async_session_maker() as session:
        result = await session.execute(
            select(Category)
            .options(selectinload(Category.children))  # Загружаем подкатегории
            .filter(Category.id == data.id)  # Фильтруем по ID категории
        )
        category = result.scalars().first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return category.children  














# @router.get ("/categories")
# async def get_all_categories():
#     async with async_session_maker() as session:
#         result = await session.execute(select(Category))
#         all_categories = result.scalars().all()
#         return all_categories
    

# @router.post("/Categoryes by id")
# async def get_category_with_subcategories_by_id(data:find_category_by_id):
#     async with async_session_maker() as session:
#         result = await session.execute(
#             select(Category)
#             .options(selectinload(Category.children)) 
#             .where(Category.id == data.id)
#         )
#         category = result.scalars().first()
#         if category:
#             return {
#                 "id": category.id,
#                 "name": category.name,
#                 "parent_name": category.parent_name,
#                 "sub_categories": [{"id": sub.id, "name": sub.name} for sub in category.children]  # Возвращаем подкатегории
#             }
#         else:
#             return {"message": f"Категория с ID {data.id} не найдена."}    