from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    number: str
    password: str
    name: str
    email:EmailStr
    
class UserLogin(BaseModel):
    number: str
    password: str