from sqlalchemy import Column, ForeignKey, MetaData, String, Boolean, Integer
from src.database import Base
from sqlalchemy.orm import relationship
from src.products.models import Product

metadata = MetaData()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")

    products = relationship("Product", back_populates="Category")