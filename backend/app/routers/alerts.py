from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.brand import Brand
from app.models.alert import Alert
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api", tags=["alerts"])

@router.get("/brands/{brand_id}/alerts")
def list_alerts(brand_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    alerts = db.query(Alert).filter(Alert.brand_id == brand_id).order_by(Alert.created_at.desc()).limit(50).all()
    return [{"id": a.id, "alert_type": a.alert_type, "message": a.message,
             "is_read": a.is_read, "created_at": a.created_at,
             "competitor_id": a.competitor_id} for a in alerts]

@router.put("/alerts/{alert_id}/read")
def mark_read(alert_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    db.commit()
    return {"success": True}
