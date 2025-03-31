from typing import List, Optional
from pydantic import BaseModel, validator
from src.categories.models import Category

class New_category(BaseModel):
    name : str
    parent_name : Optional[str] = None

class find_category_by_id(BaseModel):
    id: int    

class find_category_by_name(BaseModel):
    name : str 

  