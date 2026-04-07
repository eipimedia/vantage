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
      meta_token = os.getenv("META_ACCESS_TOKEN")
      if not meta_token:
                logger.warning(f"META_ACCESS_TOKEN not set. Returning mock data for {page_name}")
                return _get_mock_ads(page_name)
            try:
                      return _fetch_from_meta_api(page_id, page_name, meta_token, days)
except Exception as e:
        logger.error(f"Error fetching ads for {page_name}: {str(e)}")
        return _get_mock_ads(page_name)


def _fetch_from_meta_api(page_id, page_name, access_token, days):
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
    if "data" not in data:
              return []
          return [_clean_ad_object(ad, page_name) for ad in data["data"]]


def _clean_ad_object(ad, page_name):
      bodies = ad.get("ad_creative_bodies", [])
    titles = ad.get("ad_creative_link_titles", [])
    return {
              "page_name": page_name,
              "ad_id": ad.get("id", ""),
              "created_at": ad.get("ad_creation_time", ""),
              "body": (bodies[0] if bodies else "")[:200],
              "title": (titles[0] if titles else "")[:100],
              "spend_range": str(ad.get("spend", "Unknown")),
              "impression_range": str(ad.get("impressions", "Unknown")),
    }


def _get_mock_ads(page_name: str) -> list[dict]:
      return [
          {
                        "page_name": page_name, "ad_id": "mock_ad_001",
                        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                        "body": "Discover our latest collection. Built with sustainable materials.",
                        "title": "New Sustainable Collection",
                        "spend_range": "500-1000", "impression_range": "5000-10000",
          },
          {
                        "page_name": page_name, "ad_id": "mock_ad_002",
                        "created_at": (datetime.now() - timedelta(days=4)).isoformat(),
                        "body": "Weekend flash sale! Limited time offer.",
                        "title": "Flash Sale This Weekend",
                        "spend_range": "1000-2000", "impression_range": "15000-25000",
          },
          {
                        "page_name": page_name, "ad_id": "mock_ad_003",
                        "created_at": (datetime.now() - timedelta(days=6)).isoformat(),
                        "body": "5 stars - Best purchase I made this year.",
                        "title": "See What Our Customers Say",
                        "spend_range": "300-500", "impression_range": "3000-8000",
          },
]
