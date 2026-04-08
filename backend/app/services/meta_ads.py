"""
Meta Ads Library Integration Service

Fetches competitor ads from Meta Ad Library API.
Falls back to mock data when credentials are missing.
"""

import logging
import os
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)


def fetch_competitor_ads(page_id: str, page_name: str, days: int = 7) -> list[dict]:
    """
    Fetch competitor ads from Meta Ad Library API.

    Args:
        page_id: Facebook Page ID of the competitor
        page_name: Display name of the competitor
        days: Number of days to look back

    Returns:
        List of ad objects with title, body, spend_range, impression_range
    """
    meta_token = os.getenv("META_ACCESS_TOKEN")

    if not meta_token:
        logger.warning(f"META_ACCESS_TOKEN not set. Returning mock data for {page_name}")
        return _get_mock_ads(page_name)

    try:
        return _fetch_from_meta_api(page_id, page_name, meta_token, days)
    except Exception as e:
        logger.error(f"Error fetching ads for {page_name}: {str(e)}")
        return _get_mock_ads(page_name)


def _fetch_from_meta_api(page_id: str, page_name: str, access_token: str, days: int) -> list[dict]:
    """Fetch ads from Meta Ad Library API."""

    ad_delivery_date_min = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = "https://graph.facebook.com/v19.0/ads_archive"

    params = {
        "access_token": access_token,
        "search_terms": "",
        "ad_reached_countries": ["IN"],
        "search_page_ids": [page_id],
        "ad_delivery_date_min": ad_delivery_date_min,
        "fields": "id,ad_creation_time,ad_creative_bodies,ad_creative_link_titles,page_name,spend,impressions",
        "limit": 50,
    }

    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()

    data = response.json()
    ads = data.get("data", [])

    return [_clean_ad_object(ad) for ad in ads]


def _clean_ad_object(ad: dict) -> dict:
    """Clean and normalize an ad object from the API."""

    bodies = ad.get("ad_creative_bodies", [])
    titles = ad.get("ad_creative_link_titles", [])
    spend = ad.get("spend", {})
    impressions = ad.get("impressions", {})

    spend_range = ""
    if spend:
        lower = spend.get("lower_bound", "")
        upper = spend.get("upper_bound", "")
        if lower or upper:
            spend_range = f"₹{lower}-{upper}" if upper else f"₹{lower}+"

    impression_range = ""
    if impressions:
        lower = impressions.get("lower_bound", "")
        upper = impressions.get("upper_bound", "")
        if lower or upper:
            impression_range = f"{lower}-{upper}" if upper else f"{lower}+"

    return {
        "id": ad.get("id", ""),
        "title": titles[0] if titles else "",
        "body": bodies[0] if bodies else "",
        "spend_range": spend_range,
        "impression_range": impression_range,
        "created_time": ad.get("ad_creation_time", ""),
    }


def _get_mock_ads(page_name: str) -> list[dict]:
    """Return mock ads for testing when API is unavailable."""

    mock_templates = [
        {
            "id": f"mock_{page_name}_1",
            "title": f"{page_name} - Sustainable Collection",
            "body": f"Discover {page_name}'s latest eco-friendly collection. Shop now with free shipping on orders over ₹999.",
            "spend_range": "₹5000-10000",
            "impression_range": "50000-100000",
            "created_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0000"),
        },
        {
            "id": f"mock_{page_name}_2",
            "title": f"{page_name} - Flash Sale",
            "body": f"48-hour flash sale at {page_name}! Up to 40% off on selected items. Limited stock available.",
            "spend_range": "₹10000-20000",
            "impression_range": "100000-200000",
            "created_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0000"),
        },
        {
            "id": f"mock_{page_name}_3",
            "title": f"Why {page_name}?",
            "body": f"Join 2 million+ happy customers. {page_name} delivers quality you can trust, with hassle-free returns.",
            "spend_range": "₹2000-5000",
            "impression_range": "20000-50000",
            "created_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0000"),
        },
    ]

    return mock_templates
