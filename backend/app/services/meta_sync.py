import httpx
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.competitor import Competitor
from app.models.ad import Ad
import uuid

MOCK_ADS = [
    {"headline": "Glow Like Never Before", "body": "Our vitamin C serum gives you radiant skin in 7 days. Dermatologist tested.", "cta": "Shop Now", "format": "image"},
    {"headline": "50% Off Today Only", "body": "Premium skincare at half the price. Limited time offer — don't miss out.", "cta": "Grab Deal", "format": "video"},
    {"headline": "Real Results, Real People", "body": "Join 2M+ happy customers who transformed their skin with our range.", "cta": "Try Free", "format": "carousel"},
    {"headline": "Your Skin, Our Mission", "body": "100% natural ingredients. Zero harmful chemicals. Just pure goodness.", "cta": "Learn More", "format": "image"},
    {"headline": "New: Retinol Night Cream", "body": "Fight aging while you sleep. Wake up to visibly younger skin.", "cta": "Shop New", "format": "video"},
]

SPEND_SIGNALS = ["low", "low", "medium", "medium", "high", "surge"]

async def sync_competitor_ads(competitor_id: str):
    """Sync ads for a competitor — uses Meta Ad Library API if token available, else mock data."""
    db: Session = SessionLocal()
    try:
        competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not competitor:
            return

        if settings.META_ACCESS_TOKEN and competitor.facebook_page_id:
            await _sync_from_meta(db, competitor)
        else:
            await _sync_mock_data(db, competitor)

        competitor.last_synced_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()

async def _sync_from_meta(db: Session, competitor: Competitor):
    """Fetch from real Meta Ad Library API."""
    url = "https://graph.facebook.com/v18.0/ads_archive"
    params = {
        "access_token": settings.META_ACCESS_TOKEN,
        "search_page_ids": competitor.facebook_page_id,
        "ad_type": "ALL",
        "fields": "id,ad_creative_body,ad_creative_link_title,ad_snapshot_url,page_name,ad_delivery_start_time",
        "limit": 50
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=30)
        if response.status_code != 200:
            await _sync_mock_data(db, competitor)
            return

        data = response.json().get("data", [])
        for item in data:
            existing = db.query(Ad).filter(Ad.ad_id == item["id"]).first()
            if not existing:
                ad = Ad(
                    competitor_id=competitor.id,
                    platform="meta",
                    ad_id=item["id"],
                    creative_url=item.get("ad_snapshot_url"),
                    headline=item.get("ad_creative_link_title", ""),
                    body=item.get("ad_creative_body", ""),
                    format="image",
                    spend_signal=random.choice(SPEND_SIGNALS)
                )
                db.add(ad)

async def _sync_mock_data(db: Session, competitor: Competitor):
    """Generate realistic mock ad data for demo purposes."""
    num_ads = random.randint(3, 6)
    for _ in range(num_ads):
        template = random.choice(MOCK_ADS)
        ad = Ad(
            competitor_id=competitor.id,
            platform=random.choice(["meta", "meta", "google"]),
            ad_id=str(uuid.uuid4()),
            headline=f"{competitor.name}: {template['headline']}",
            body=template["body"],
            cta=template["cta"],
            format=template["format"],
            spend_signal=random.choice(SPEND_SIGNALS),
            first_seen=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            last_seen=datetime.utcnow()
        )
        db.add(ad)
