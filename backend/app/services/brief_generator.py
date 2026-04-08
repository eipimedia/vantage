"""
Intelligence Brief Generation Service

Uses OpenAI GPT-4o-mini to generate structured competitive intelligence briefs.
Falls back to mock briefs when API key is unavailable.
"""

import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_brief(client_name: str, competitors_data: list[dict]) -> dict:
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not set. Returning mock brief.")
        return _get_mock_brief(client_name, competitors_data)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        return _generate_with_openai(client, client_name, competitors_data)
    except ImportError:
        return _get_mock_brief(client_name, competitors_data)
    except Exception as e:
        logger.error(f"Error generating brief: {str(e)}")
        return _get_mock_brief(client_name, competitors_data)


def _generate_with_openai(client, client_name, competitors_data):
    context = _build_competitors_context(competitors_data)
    now = datetime.now()
    week_str = f"W{now.isocalendar()[1]} {now.year}"

    prompt = f"""You are a competitive intelligence analyst for {client_name}.
Analyze this competitor ad data and return a JSON brief.

Week: {week_str}
Data: {context}

Return JSON with these exact keys: week, summary, competitors (list with name/signal/headline/detail/watch/ad_count/tags), recommendations (list with priority/title/detail).
Signal values must be one of: high, medium, low, opportunity."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    brief = json.loads(response.choices[0].message.content)
    return brief if _validate_brief(brief) else _get_mock_brief(client_name, competitors_data)


def _build_competitors_context(competitors_data):
    parts = []
    for comp in competitors_data:
        ads = comp.get("ads", [])
        parts.append(f"{comp.get('name')}: {len(ads)} ads")
        for ad in ads[:3]:
            parts.append(f"  - {ad.get('title','')} | {ad.get('body','')[:60]}")
    return "\n".join(parts)


def _validate_brief(brief):
    if not all(k in brief for k in ["week", "summary", "competitors", "recommendations"]):
        return False
    return all(c.get("signal") in ["high", "medium", "low", "opportunity"] for c in brief.get("competitors", []))


def _get_mock_brief(client_name, competitors_data):
    now = datetime.now()
    week_str = f"W{now.isocalendar()[1]} {now.year}"

    comps = []
    for comp in competitors_data[:4]:
        n = comp.get("name", "Unknown")
        count = len(comp.get("ads", []))
        sig = "high" if count > 20 else "medium" if count > 10 else "low"
        comps.append({
            "name": n,
            "signal": sig,
            "headline": f"{n}: {sig.upper()} activity",
            "detail": f"Observed {count} ads in the past 7 days.",
            "watch": f"Monitor {n} for shifts" if count > 0 else None,
            "ad_count": count,
            "tags": ["Active" if count > 5 else "Low"],
        })

    return {
        "week": week_str,
        "summary": f"Competitive landscape for {client_name} shows varied activity. Key opportunities available.",
        "competitors": comps,
        "recommendations": [
            {"priority": 1, "title": "Price Audit", "detail": "Review pricing vs competitor promotions."},
            {"priority": 2, "title": "Creative Refresh", "detail": "Counter competitor creatives with differentiated messaging."},
            {"priority": 3, "title": "Audience Expansion", "detail": "Target gaps in competitor coverage."},
        ],
    }
