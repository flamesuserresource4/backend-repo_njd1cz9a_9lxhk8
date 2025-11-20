import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Offer

app = FastAPI(title="MFO Offers API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OfferCreate(Offer):
    pass


class OfferPublic(Offer):
    id: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "MFO Offers API running"}


@app.get("/api/offers", response_model=List[OfferPublic])
def list_offers(
    q: Optional[str] = Query(None, description="Search by name or tag"),
    max_apr: Optional[float] = Query(None, ge=0, description="Filter by max APR %"),
    min_amount: Optional[int] = Query(None, ge=0, description="Minimum amount required"),
    max_amount: Optional[int] = Query(None, ge=0, description="Maximum amount allowed"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_dict = {}

    # Range filters
    if max_apr is not None:
        filter_dict["apr"] = {"$lte": max_apr}
    if min_amount is not None:
        filter_dict.setdefault("max_amount", {})
        filter_dict["max_amount"].update({"$gte": min_amount})
    if max_amount is not None:
        filter_dict.setdefault("min_amount", {})
        filter_dict["min_amount"].update({"$lte": max_amount})
    if min_rating is not None:
        filter_dict["rating"] = {"$gte": min_rating}

    # Text/tag search
    if q:
        filter_dict["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"tags": {"$in": [q]}}
        ]

    docs = get_documents("offer", filter_dict)

    # Convert ObjectId to string and map to public model
    results = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        results.append(OfferPublic(**d))
    return results


@app.post("/api/offers", status_code=201)
def create_offer(payload: OfferCreate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    inserted_id = create_document("offer", payload)
    return {"id": inserted_id}


@app.post("/api/offers/seed")
def seed_offers():
    """Seed database with a curated list of MFO offers (idempotent)."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        count = db["offer"].count_documents({})
        if count > 0:
            return {"status": "ok", "inserted": 0, "message": "Offers already exist"}

        sample = [
            {
                "name": "Быстрые Деньги",
                "apr": 29.9,
                "min_amount": 1000,
                "max_amount": 50000,
                "term_min_days": 7,
                "term_max_days": 30,
                "approval_rate": 85.0,
                "rating": 4.6,
                "description": "Мгновенное одобрение и выдача на карту за 5 минут.",
                "link": "https://example.com/fast",
                "tags": ["быстро", "онлайн", "на карту"],
            },
            {
                "name": "Надёжный Займ",
                "apr": 24.5,
                "min_amount": 3000,
                "max_amount": 70000,
                "term_min_days": 10,
                "term_max_days": 60,
                "approval_rate": 78.0,
                "rating": 4.4,
                "description": "Без справок и поручителей, прозрачные условия.",
                "link": "https://example.com/reliable",
                "tags": ["без справок", "прозрачно"],
            },
            {
                "name": "Займер",
                "apr": 19.9,
                "min_amount": 5000,
                "max_amount": 100000,
                "term_min_days": 15,
                "term_max_days": 90,
                "approval_rate": 70.0,
                "rating": 4.8,
                "description": "Лучшие ставки для постоянных клиентов.",
                "link": "https://example.com/zaimer",
                "tags": ["низкая ставка", "лояльность"],
            },
            {
                "name": "РубльGo",
                "apr": 34.9,
                "min_amount": 1000,
                "max_amount": 30000,
                "term_min_days": 7,
                "term_max_days": 45,
                "approval_rate": 90.0,
                "rating": 4.2,
                "description": "Высокий процент одобрения, первый займ под 0%.",
                "link": "https://example.com/rublgo",
                "tags": ["0%", "высокое одобрение"],
            },
        ]

        inserted = 0
        for s in sample:
            create_document("offer", s)
            inserted += 1

        return {"status": "ok", "inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
