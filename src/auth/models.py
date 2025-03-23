from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, MetaData, String, Boolean, Integer
from src.database import Base
from sqlalchemy.orm import relationship

metadata = MetaData()

class Tokens(Base):
    __tablename__ = "tokens"  

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    
    user = relationship("User", back_populates="tokens") 