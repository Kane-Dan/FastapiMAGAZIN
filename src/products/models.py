from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, MetaData, String, Boolean, Integer
from src.database import Base
from sqlalchemy.orm import relationship

metadata = MetaData()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    picture = Column(String, nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")