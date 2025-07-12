from sqlalchemy import Column, Integer,DateTime, String, ForeignKey, func, Enum, Boolean
from sqlalchemy.orm import relationship
import enum


from app.core.database import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    

    books = relationship("Book", back_populates="author", cascade="all, delete")