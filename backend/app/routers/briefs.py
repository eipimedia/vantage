from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.brand import Brand
from app.models.brief import WeeklyBrief
from app.routers.deps import get_current_user
from app.models.user import User
from app.services.ai import generate_weekly_brief

router = APIRouter(prefix="/api", tags=["briefs"])

@router.get("/brands/{brand_id}/briefs")
def list_briefs(brand_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    briefs = db.query(WeeklyBrief).filter(WeeklyBrief.brand_id == brand_id).order_by(WeeklyBrief.generated_at.desc()).all()
    return [{"id": b.id, "week_start": b.week_start, "week_end": b.week_end,
             "key_insights": b.key_insights, "recommendations": b.recommendations,
             "generated_at": b.generated_at} for b in briefs]

@router.get("/brands/{brand_id}/briefs/latest")
def latest_brief(brand_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    brief = db.query(WeeklyBrief).filter(WeeklyBrief.brand_id == brand_id).order_by(WeeklyBrief.generated_at.desc()).first()
    if not brief:
        return None
    return {"id": brief.id, "week_start": brief.week_start, "week_end": brief.week_end,
            "content": brief.content, "key_insights": brief.key_insights,
            "recommendations": brief.recommendations, "generated_at": brief.generated_at}

@router.get("/briefs/{brief_id}")
def get_brief(brief_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brief = db.query(WeeklyBrief).filter(WeeklyBrief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return {"id": brief.id, "week_start": brief.week_start, "week_end": brief.week_end,
            "content": brief.content, "key_insights": brief.key_insights,
            "recommendations": brief.recommendations, "generated_at": brief.generated_at}

@router.post("/brands/{brand_id}/briefs/generate")
def trigger_brief(brand_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    background_tasks.add_task(generate_weekly_brief, brand_id)
    return {"success": True, "message": "Brief generation started"}
