from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Genre(str, enum.Enum):
    fiction = "Fiction"
    nonfiction = "Non-Fiction"
    science = "Science"
    history = "History"

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    published_year = Column(Integer, nullable=False)
    genre = Column(Enum(Genre), nullable=False)

    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    author = relationship("Author", back_populates="books")
