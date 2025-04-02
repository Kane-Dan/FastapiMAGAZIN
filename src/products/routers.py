from fastapi import APIRouter
from sqlalchemy import select
from src.products.schemas import Products_shema
from src.database import async_session_maker 
from src.products.models import Product

router = APIRouter()


@router.get("/products")
async def  get_all_porducts():
    async with async_session_maker() as session:
        result = await session.execute(select(Product))
        all_products = result.scalars().all()
        return all_products
    
    