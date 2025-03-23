from pydantic import BaseModel

class Token_Access(BaseModel):
    id : int
    user_id : int
    token : str
    