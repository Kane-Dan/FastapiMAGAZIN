from pydantic import BaseModel

class Products(BaseModel):
    picture:str
    name:str
    description:str
    price:int
