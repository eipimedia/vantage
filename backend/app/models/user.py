from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    subscription_tier = Column(String, default="starter")  # starter, growth, pro
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    brands = relationship("Brand", back_populates="user", cascade="all, delete-orphan")
