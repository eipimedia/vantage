from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.brand import Brand
from app.models.ad import Ad
from app.models.competitor import Competitor
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api", tags=["ads"])

@router.get("/brands/{brand_id}/ads")
def list_ads(
    brand_id: str,
    competitor_id: Optional[str] = None,
    platform: Optional[str] = None,
    format: Optional[str] = None,
    spend_signal: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    competitor_ids = [c.id for c in brand.competitors]
    if not competitor_ids:
        return {"ads": [], "total": 0}

    query = db.query(Ad).filter(Ad.competitor_id.in_(competitor_ids))

    if competitor_id:
        query = query.filter(Ad.competitor_id == competitor_id)
    if platform:
        query = query.filter(Ad.platform == platform)
    if format:
        query = query.filter(Ad.format == format)
    if spend_signal:
        query = query.filter(Ad.spend_signal == spend_signal)

    total = query.count()
    ads = query.order_by(Ad.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for a in ads:
        competitor = db.query(Competitor).filter(Competitor.id == a.competitor_id).first()
        result.append({
            "id": a.id, "platform": a.platform, "ad_id": a.ad_id,
            "creative_url": a.creative_url, "headline": a.headline,
            "body": a.body, "cta": a.cta, "format": a.format,
            "spend_signal": a.spend_signal, "is_active": a.is_active,
            "first_seen": a.first_seen, "last_seen": a.last_seen,
            "ai_analysis": a.ai_analysis,
            "competitor_name": competitor.name if competitor else None,
            "competitor_id": a.competitor_id
        })

    return {"ads": result, "total": total}

@router.get("/ads/{ad_id}")
def get_ad(ad_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return {"id": ad.id, "platform": ad.platform, "headline": ad.headline,
            "body": ad.body, "cta": ad.cta, "format": ad.format,
            "spend_signal": ad.spend_signal, "creative_url": ad.creative_url,
            "ai_analysis": ad.ai_analysis, "first_seen": ad.first_seen}
