from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Ad(Base):
    __tablename__ = "ads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    competitor_id = Column(String, ForeignKey("competitors.id"), nullable=False)
    platform = Column(String, nullable=False)  # meta, google
    ad_id = Column(String)  # external ID from platform
    creative_url = Column(String)
    headline = Column(String)
    body = Column(String)
    cta = Column(String)
    format = Column(String)  # image, video, carousel
    spend_signal = Column(String, default="low")  # low, medium, high, surge
    is_active = Column(Boolean, default=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    ai_analysis = Column(JSON)  # GPT-4o Vision analysis results
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    competitor = relationship("Competitor", back_populates="ads")
