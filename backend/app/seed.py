"""Seed script — run with: python -m app.seed"""
from datetime import datetime, timedelta
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models import *
from app.core.database import Base
import uuid

Base.metadata.create_all(bind=engine)

SAMPLE_BRIEF = """## Weekly Competitive Intelligence Brief
**Mamaearth | Week of March 24–31, 2026**

---

## Executive Summary

The Indian skincare competitive landscape showed heightened activity this week, with WOW Skin Science running a surge-level paid push on Meta — their highest volume in 6 weeks. Plum Goodness pivoted messaging toward sustainability credentials, and mCaffeine continued their aggressive video-first strategy on Instagram. Mamaearth should prioritize defensive positioning against WOW's discount assault while building on its natural ingredients narrative.

## Key Observations

**WOW Skin Science** ran 14 new creatives this week, up from 5 last week — a 180% surge. Eight of these feature aggressive discount messaging (40–60% off), carousel formats dominating. This pattern typically signals a quarterly acquisition push or an attempt to clear inventory ahead of a new product launch. WOW's Google spend also ticked up, with search ads targeting "best vitamin C serum" — a keyword Mamaearth has traditionally owned.

**Plum Goodness** launched 6 new image ads with a unified sustainability theme: "Clean Beauty, Clear Conscience." Their CTA shifted from "Shop Now" to "Join the Movement," indicating a brand-building phase rather than pure conversion. This is a medium-spend week for Plum — they're playing the long game on brand equity while keeping conversion campaigns running quietly.

**mCaffeine** continues their video-first strategy with 9 new reels-style creatives this week. All feature under-30 talent in lifestyle settings, strong voiceover, and a consistent "Powered by Caffeine" brand hook. Their of retention-focused messaging ("Your skin's morning ritual") suggests they're targeting existing customers for upsell, not cold acquisition.

## Emerging Trends

Three patterns are clear across the competitive set this week. First, discount-led creative is peaking — WOW's surge signals a category-wide promotional moment that Mamaearth may need to respond to or risk losing price-sensitive customers. Second, video is winning: mCaffeine's consistent video investment and WOW's increasing reel production suggest Meta's algorithm is rewarding video format heavily in the skincare category right now. Third, sustainability messaging is becoming table stakes — Plum's pivot signals this is moving from differentiator to baseline expectation.

## Strategic Recommendations

**1. Run a short-burst counter-campaign to WOW's discount push.** WOW's surge spend is targeting price-sensitive buyers. A 48–72 hour flash offer on Mamaearth's hero SKUs (Vitamin C serum, Onion shampoo) with strong Meta placement would capture buyers currently in-market before WOW converts them. Budget: ₹8–12L for the burst.

**2. Increase video creative output to 60% of new ad production this week.** mCaffeine and WOW are both signaling that video is performing. Mamaearth's current creative mix is 40% video — flipping this ratio over the next 2 weeks aligns with where the Meta algorithm is pushing reach in the category.

**3. Launch a natural ingredients storytelling series before Plum owns the sustainability conversation.** Plum's pivot is early-stage — Mamaearth has a 2–3 week window to move first with a stronger, more specific sustainability narrative (ingredient sourcing stories, certifications, zero-plastic packaging). Own it before it becomes Plum's.
"""

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "demo@getvantage.io").first():
            print("Already seeded.")
            return

        # Create demo user
        user = User(
            id=str(uuid.uuid4()),
            email="demo@getvantage.io",
            name="Rohit Reddy",
            password_hash=get_password_hash("demo123"),
            subscription_tier="growth"
        )
        db.add(user)

        # Create brand
        brand = Brand(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name="Mamaearth",
            website="https://mamaearth.in",
            category="Skincare & Personal Care"
        )
        db.add(brand)

        # Create competitors
        competitors_data = [
            {"name": "WOW Skin Science", "website": "https://buywow.in", "facebook_page_id": "123456"},
            {"name": "Plum Goodness", "website": "https://plumgoodness.com", "facebook_page_id": "234567"},
            {"name": "mCaffeine", "website": "https://mcaffeine.com", "facebook_page_id": "345678"},
        ]

        competitors = []
        for cd in competitors_data:
            c = Competitor(
                id=str(uuid.uuid4()),
                brand_id=brand.id,
                name=cd["name"],
                website=cd["website"],
                facebook_page_id=cd["facebook_page_id"],
                last_synced_at=datetime.utcnow()
            )
            db.add(c)
            competitors.append(c)

        db.flush()

        # Create mock ads
        ad_templates = [
            ("Glow Like Never Before", "Our vitamin C serum delivers radiant skin in 7 days. Dermatologist tested & approved.", "Shop Now", "image", "medium"),
            ("50% Off Today Only", "Premium skincare at half the price. Don't miss this limited time offer.", "Grab Deal", "carousel", "surge"),
            ("Real Results, Real People", "Join 2M+ happy customers who transformed their skin naturally.", "Try Free", "video", "high"),
            ("Your Skin, Our Mission", "100% natural ingredients. Zero harmful chemicals. Pure goodness.", "Learn More", "image", "low"),
            ("New: Retinol Night Cream", "Fight aging while you sleep. Wake up to visibly younger skin.", "Shop New", "video", "medium"),
            ("Dermatologist Approved", "Clinically tested formula. Safe for sensitive skin. Trusted by experts.", "See Results", "image", "low"),
            ("Flash Sale: 48 Hours", "Up to 60% off sitewide. Free delivery on orders above ₹495.", "Shop Now", "carousel", "surge"),
            ("The Natural Choice", "No sulfates. No parabens. No compromise on results.", "Switch Now", "image", "medium"),
        ]

        for i, comp in enumerate(competitors):
            for j, (headline, body, cta, format, signal) in enumerate(ad_templates[:5 + i]):
                ad = Ad(
                    id=str(uuid.uuid4()),
                    competitor_id=comp.id,
                    platform="meta" if j % 3 != 2 else "google",
                    ad_id=f"mock_{comp.id[:8]}_{j}",
                    headline=f"{comp.name}: {headline}",
                    body=body,
                    cta=cta,
                    format=format,
                    spend_signal=signal,
                    is_active=True,
                    first_seen=datetime.utcnow() - timedelta(days=j * 2 + 1),
                    last_seen=datetime.utcnow()
                )
                db.add(ad)

        # Create sample brief
        brief = WeeklyBrief(
            id=str(uuid.uuid4()),
            brand_id=brand.id,
            week_start=datetime.utcnow() - timedelta(days=7),
            week_end=datetime.utcnow(),
            content=SAMPLE_BRIEF,
            key_insights=[
                "WOW Skin Science running a surge-level ad push — 180% increase week-over-week",
                "Plum Goodness pivoting to sustainability messaging with new 'Clean Beauty' campaign",
                "mCaffeine doubling down on video format — all 9 new ads are video/reels",
                "Category-wide trend toward discount messaging signals promotional moment"
            ],
            recommendations=[
                "Run 48–72 hour counter-campaign against WOW's discount push (₹8–12L budget)",
                "Flip creative mix to 60% video to align with Meta algorithm trends",
                "Launch sustainability storytelling series before Plum owns the narrative"
            ]
        )
        db.add(brief)

        # Create sample alerts
        alerts_data = [
            ("surge", "WOW Skin Science ad spend surged 180% this week — 14 new creatives detected", competitors[0].id),
            ("new_format", "Plum Goodness launched first carousel ads targeting sustainability messaging", competitors[1].id),
            ("messaging_pivot", "mCaffeine shifted CTA from 'Shop Now' to 'Start Your Ritual' — retention focus", competitors[2].id),
        ]

        for alert_type, message, comp_id in alerts_data:
            alert = Alert(
                id=str(uuid.uuid4()),
                brand_id=brand.id,
                competitor_id=comp_id,
                alert_type=alert_type,
                message=message,
                is_read=False
            )
            db.add(alert)

        db.commit()
        print("✅ Seed complete. Login: demo@getvantage.io / demo123")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
