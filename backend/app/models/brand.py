from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    website = Column(String)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="brands")
    competitors = relationship("Competitor", back_populates="brand", cascade="all, delete-orphan")
    briefs = relationship("WeeklyBrief", back_populates="brand", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="brand", cascade="all, delete-orphan")
