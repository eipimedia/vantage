"""
API Routes for Intelligence Brief Generation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from app.services.meta_ads import fetch_competitor_ads
from app.services.brief_generator import generate_brief
from app.services.email_sender import send_brief_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/brief", tags=["brief"])

DEMO_COMPETITORS = {
    "zouk": [
        {"name": "Mokobara", "page_id": "104793371592697"},
        {"name": "Uppercase", "page_id": "111543574345721"},
        {"name": "Wildcraft", "page_id": "116392925058"},
        {"name": "Lavie", "page_id": "178203785561385"},
    ],
    "default": [
        {"name": "Mokobara", "page_id": "104793371592697"},
        {"name": "Uppercase", "page_id": "111543574345721"},
        {"name": "Wildcraft", "page_id": "116392925058"},
    ],
}


class CompetitorInput(BaseModel):
    name: str
    page_id: str


class GenerateBriefRequest(BaseModel):
    client_name: str
    competitors: list[CompetitorInput]
    email: EmailStr


class BriefResponse(BaseModel):
    week: str
    summary: str
    competitors: list[dict]
    recommendations: list[dict]


@router.post("/generate", response_model=BriefResponse)
async def generate_and_send_brief(request: GenerateBriefRequest) -> dict:
    """Generate an intelligence brief and send via email."""
    try:
        if not request.competitors:
            raise HTTPException(status_code=400, detail="At least one competitor required")
        if len(request.competitors) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 competitors per request")

        competitors_data = []
        for comp in request.competitors:
            ads = fetch_competitor_ads(page_id=comp.page_id, page_name=comp.name, days=7)
            competitors_data.append({"name": comp.name, "page_id": comp.page_id, "ads": ads})

        brief = generate_brief(request.client_name, competitors_data)
        email_sent = send_brief_email(to_email=request.email, client_name=request.client_name, brief=brief)

        if not email_sent:
            logger.warning(f"Failed to send email to {request.email}")

        return brief

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating brief: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate brief")


@router.get("/preview/{client_name}", response_model=BriefResponse)
async def preview_brief(client_name: str) -> dict:
    """Get a preview brief without sending email."""
    try:
        client_key = client_name.lower().strip()
        demo_comps = DEMO_COMPETITORS.get(client_key, DEMO_COMPETITORS.get("default"))

        if not demo_comps:
            raise HTTPException(status_code=400, detail=f"No demo data for '{client_name}'")

        competitors_data = []
        for comp in demo_comps:
            ads = fetch_competitor_ads(page_id=comp["page_id"], page_name=comp["name"], days=7)
            competitors_data.append({"name": comp["name"], "page_id": comp["page_id"], "ads": ads})

        brief = generate_brief(client_name, competitors_data)
        return brief

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate preview brief")


@router.get("/available-clients")
async def list_available_clients() -> dict:
    """List available demo clients."""
    return {
        "clients": list(DEMO_COMPETITORS.keys()),
        "message": "Use /brief/preview/{client_name} to get a preview brief",
    }


@router.post("/competitors/list")
async def list_competitors(client_name: str) -> dict:
    """List competitors for a given client."""
    client_key = client_name.lower().strip()
    demo_comps = DEMO_COMPETITORS.get(client_key, DEMO_COMPETITORS.get("default"))

    if not demo_comps:
        raise HTTPException(status_code=400, detail=f"No demo data for '{client_name}'")

    return {"client_name": client_name, "competitors": demo_comps, "count": len(demo_comps)}
