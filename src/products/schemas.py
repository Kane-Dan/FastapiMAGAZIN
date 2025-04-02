from pydantic import BaseModel

class Products_shema(BaseModel):
    picture:str
    name:str
    description:str
    price:int
    category_name : str

class Product_by_id(BaseModel):
    id:int