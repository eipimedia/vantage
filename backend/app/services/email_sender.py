# Email Delivery Service
# Sends intelligence briefs via Resend API.

import logging
import os
import httpx

logger = logging.getLogger(__name__)

CYAN = "#00D4FF"
NAVY = "#05091A"


def send_brief_email(to_email: str, client_name: str, brief: dict) -> bool:
      api_key = os.getenv("RESEND_API_KEY")
      if not api_key:
                logger.warning(f"RESEND_API_KEY not set. Skipping email to {to_email}.")
                return True
            try:
                      html = _build_html(client_name, brief)
                      subject = f"Vantage Brief — {client_name} | {brief.get('week', 'Weekly')}"
                      return _send(api_key, to_email, subject, html)
except Exception as e:
        logger.error(f"Email error: {str(e)}")
        return False


def _send(api_key, to_email, subject, html):
      r = httpx.post(
          "https://api.resend.com/emails",
          json={
                        "from": "briefs@vantage-liart-one.vercel.app",
                        "to": to_email,
                        "subject": subject,
                        "html": html,
          },
          headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
          timeout=10.0,
)
    r.raise_for_status()
    logger.info(f"Email sent to {to_email}")
    return True


def _build_html(client_name, brief):
      week = brief.get("week", "")
    summary = brief.get("summary", "")
    competitors = brief.get("competitors", [])
    recommendations = brief.get("recommendations", [])

    comp_html = ""
    for c in competitors:
              sig = c.get("signal", "low")
              colors = {
                  "high": "#EF4444", "medium": "#F59E0B",
                  "low": "#10B981", "opportunity": "#3B82F6"
              }
              sig_color = colors.get(sig, "#6B7280")
              tags_html = " ".join(
                  f'<span style="background:#E5E7EB;color:#374151;padding:3px 8px;'
                  f'border-radius:4px;font-size:11px;">{t}</span>'
                  for t in c.get("tags", [])
              )
              watch_html = ""
              if c.get("watch"):
                            watch_html = (
                                              f'<p style="padding:8px;background:#FEF3C7;border-left:3px solid #F59E0B;'
                                              f'font-size:12px;"><b>Watch:</b> {c["watch"]}</p>'
                            )
                        comp_html += (
                                      f'<div style="border:1px solid #E5E7EB;border-radius:8px;padding:14px;margin-bottom:16px;">'
                                      f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
                                      f'<b>{c.get("name", "")}</b>'
                                      f'<span style="background:{sig_color};color:white;padding:4px 10px;'
                                      f'border-radius:20px;font-size:11px;">{sig.upper()}</span></div>'
                                      f'<p style="color:#666;font-size:13px;">{c.get("headline", "")}</p>'
                                      f'<p style="color:#777;font-size:13px;">{c.get("detail", "")}</p>'
                                      f'<p style="font-size:12px;color:#888;">{c.get("ad_count", 0)} ads / 7 days</p>'
                                      f'<div>{tags_html}</div>{watch_html}</div>'
                        )

    rec_html = ""
    for r in recommendations:
              rec_html += (
                  f'<div style="padding:10px;border-left:4px solid {CYAN};'
                  f'background:#F0FFFE;margin-bottom:12px;">'
                  f'<b>P{r.get("priority")} — {r.get("title", "")}</b>'
                  f'<p style="color:#555;font-size:12px;margin:4px 0 0;">{r.get("detail", "")}</p></div>'
    )

    return (
              f"<!DOCTYPE html><html><head><meta charset='UTF-8'></head>"
              f"<body style='font-family:sans-serif;background:#F8F9FA;padding:20px;'>"
              f"<div style='max-width:580px;margin:0 auto;background:white;border-radius:10px;overflow:hidden;'>"
              f"<div style='background:{NAVY};color:white;padding:28px;text-align:center;'>"
              f"<h1 style='margin:0;'>Vantage Intelligence Brief</h1>"
              f"<p style='margin:6px 0 0;opacity:.8;font-size:13px;'>{week} — {client_name}</p></div>"
              f"<div style='padding:24px;'>"
              f"<div style='background:#F0FFFE;border:1px solid {CYAN};border-radius:6px;padding:14px;margin-bottom:24px;'>"
              f"<p style='color:{CYAN};font-size:11px;font-weight:600;text-transform:uppercase;'>Executive Summary</p>"
              f"<p style='color:#555;font-size:13px;line-height:1.6;'>{summary}</p></div>"
              f"<h2 style='font-size:15px;border-bottom:2px solid {CYAN};padding-bottom:6px;'>Competitor Analysis</h2>"
              f"{comp_html}"
              f"<h2 style='font-size:15px;border-bottom:2px solid {CYAN};padding-bottom:6px;'>Recommendations</h2>"
              f"{rec_html}"
              f"</div>"
              f"<div style='background:#F8F9FA;padding:16px;text-align:center;font-size:11px;color:#888;'>"
              f"Vantage Competitive Intelligence</div></div></body></html>"
    )
