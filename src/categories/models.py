from sqlalchemy import Column, ForeignKey, MetaData, String, Boolean, Integer
from src.database import Base
from sqlalchemy.orm import relationship


metadata = MetaData()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True) 
    parent_name = Column(String, ForeignKey("categories.name"), nullable=True)  

    
    parent = relationship(
        "Category",
        remote_side=[name], 
        back_populates="children"
    )
    children = relationship(
        "Category",
        back_populates="parent"
    )

    products = relationship("Product", back_populates="category")
