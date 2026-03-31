from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.models.brand import Brand
from app.models.ad import Ad
from app.models.alert import Alert
from app.routers.deps import get_current_user
from app.models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/brands", tags=["brands"])

class BrandCreate(BaseModel):
    name: str
    website: Optional[str] = None
    category: Optional[str] = None

@router.get("")
def list_brands(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brands = db.query(Brand).filter(Brand.user_id == current_user.id).all()
    return [{"id": b.id, "name": b.name, "website": b.website, "category": b.category, "created_at": b.created_at} for b in brands]

@router.post("")
def create_brand(req: BrandCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = Brand(user_id=current_user.id, name=req.name, website=req.website, category=req.category)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return {"id": brand.id, "name": brand.name, "website": brand.website, "category": brand.category}

@router.get("/{brand_id}")
def get_brand(brand_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"id": brand.id, "name": brand.name, "website": brand.website, "category": brand.category}

@router.get("/{brand_id}/dashboard")
def get_dashboard(brand_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    one_week_ago = datetime.utcnow() - timedelta(days=7)
    competitor_ids = [c.id for c in brand.competitors]

    new_ads_this_week = db.query(Ad).filter(
        Ad.competitor_id.in_(competitor_ids),
        Ad.created_at >= one_week_ago
    ).count() if competitor_ids else 0

    surge_count = db.query(Ad).filter(
        Ad.competitor_id.in_(competitor_ids),
        Ad.spend_signal == "surge",
        Ad.created_at >= one_week_ago
    ).count() if competitor_ids else 0

    unread_alerts = db.query(Alert).filter(
        Alert.brand_id == brand_id,
        Alert.is_read == False
    ).count()

    recent_ads = db.query(Ad).filter(
        Ad.competitor_id.in_(competitor_ids)
    ).order_by(Ad.created_at.desc()).limit(5).all() if competitor_ids else []

    return {
        "active_competitors": len(brand.competitors),
        "new_ads_this_week": new_ads_this_week,
        "spend_surges": surge_count,
        "unread_alerts": unread_alerts,
        "recent_ads": [{"id": a.id, "headline": a.headline, "platform": a.platform,
                        "spend_signal": a.spend_signal, "format": a.format,
                        "created_at": a.created_at} for a in recent_ads]
    }
