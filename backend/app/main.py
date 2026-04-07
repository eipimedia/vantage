from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth, brands, competitors, ads, briefs, alerts
from app.routers.brief import router as brief_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vantage API", version="1.0.0", description="Competitor intelligence platform for B2C brands")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(brands.router)
app.include_router(competitors.router)
app.include_router(ads.router)
app.include_router(briefs.router)
app.include_router(alerts.router)
app.include_router(brief_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "vantage-api"}

@app.on_event("startup")
async def startup():
    print("🚀 Vantage API running")
