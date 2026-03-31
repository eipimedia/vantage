from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False)
    name = Column(String, nullable=False)
    website = Column(String)
    facebook_page_id = Column(String)
    instagram_handle = Column(String)
    google_advertiser_id = Column(String)
    last_synced_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    brand = relationship("Brand", back_populates="competitors")
    ads = relationship("Ad", back_populates="competitor", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="competitor")
