from sqlalchemy import Column, DateTime, MetaData, String, Boolean, Integer
from src.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import EmailStr
metadata = MetaData()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Отношение к таблице Tokens
    tokens = relationship("Tokens", back_populates="user")