from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

SENTRY_DSN = os.environ.get("SENTRY_DSN", "").strip()
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "production").strip()
SENTRY_RELEASE = os.environ.get("SENTRY_RELEASE", "").strip() or None
SENTRY_TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        release=SENTRY_RELEASE,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

# Bump this to wipe + reseed products & campaigns on next startup
SEED_VERSION = "aegis-v4-orders-hidden-and-legacy-fifth-item"

app = FastAPI(title="AEGIS API — Strength in Order")
api_router = APIRouter(prefix="/api")


# ---------- MODELS ----------
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    name: str
    short: str                   # short tagline / subtitle
    category: str                # tshirt, hoodie, hat, sticker, patch, coin, tumbler
    division: str                # core | legacy
    is_award_only: bool = False  # legacy items require unlock code
    price: float
    description: str
    images: List[str] = []
    accent: str = "#D4AF37"
    sizes: List[str] = []
    colors: List[str] = []
    badge: Optional[str] = None
    featured: bool = False


class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    slug: str
    name: str
    status: str                  # active | coming_soon | classified
    tagline: str
    description: str
    accent: str
    image: str
    bullets: List[str] = []
    is_unlocked: bool = True


class RedeemIn(BaseModel):
    code: str


class LegacyRequestIn(BaseModel):
    full_name: str
    email: str
    unit: Optional[str] = ""
    story: str


class ContactIn(BaseModel):
    full_name: str
    email: str
    subject: Optional[str] = ""
    message: str


class OrderItemIn(BaseModel):
    product_id: str
    quantity: int = 1
    size: Optional[str] = None
    color: Optional[str] = None


class OrderBaseIn(BaseModel):
    items: List[OrderItemIn]
    origin_url: str
    customer_name: str
    customer_email: str
    address_line1: str
    city: str
    state: str
    zip_code: str
    address_line2: Optional[str] = ""
    notes: Optional[str] = ""


class ManualOrderIn(OrderBaseIn):
    pass


class CheckoutSessionIn(OrderBaseIn):
    pass


# ---------- SEED DATA ----------
SIZES = ["S", "M", "L", "XL", "2XL", "3XL"]

CORE_PRODUCTS_RAW = [
    {
        "slug": "tactical-white-tee",
        "name": "AEGIS Tactical White Tee",
        "short": "The Foundation. Bone white. Heavyweight.",
        "category": "tshirt",
        "price": 34.0,
        "images": ["/aegis/tactical-white-tee.jpg"],
        "accent": "#C7CCD4",
        "sizes": SIZES,
        "colors": ["Bone White"],
        "badge": "BESTSELLER",
        "featured": True,
        "description": "AEGIS CORE — Tactical White. Bone-white heavyweight cotton with the AEGIS chestplate on the front and the full CORE shield on the back. Stitched flag on the sleeve. Built for the line, made to last beyond it.",
    },
    {
        "slug": "tactical-black-tee",
        "name": "AEGIS Tactical Black Tee",
        "short": "Bronze on black. Discipline you can wear.",
        "category": "tshirt",
        "price": 34.0,
        "images": ["/aegis/core-black-tee.jpg"],
        "accent": "#B08B4F",
        "sizes": SIZES,
        "colors": ["Black"],
        "badge": "NEW",
        "featured": True,
        "description": "AEGIS CORE — Tactical Black. Antique bronze CORE crest on midnight black, USA flag on sleeve. The everyday uniform of the Order. Heavyweight, pre-shrunk, riot-rated.",
    },
    {
        "slug": "core-hoodie-black",
        "name": "AEGIS CORE Hoodie — Midnight",
        "short": "Tactical winter loadout.",
        "category": "hoodie",
        "price": 64.0,
        "images": ["/aegis/core-badge.jpg"],
        "accent": "#4A7FC1",
        "sizes": SIZES,
        "colors": ["Midnight Black"],
        "featured": True,
        "description": "Heavyweight midnight black pullover with the CORE shield emblazoned across the back. 12oz fleece, kangaroo pouch, ribbed cuffs. Designed for cold yard mornings and post-shift cooldown.",
    },
    {
        "slug": "core-hat-flexfit",
        "name": "AEGIS CORE Flexfit Cap",
        "short": "Low profile. High discipline.",
        "category": "hat",
        "price": 28.0,
        "images": ["/aegis/core-badge.jpg"],
        "accent": "#4A7FC1",
        "sizes": ["S/M", "L/XL"],
        "colors": ["Black"],
        "description": "Structured low-profile flexfit cap. Embroidered AEGIS shield on the crown. Standard issue daily wear.",
    },
]

# Legacy items — awarded, not sold. Visible but require redeem code.
LEGACY_PRODUCTS_RAW = [
    {
        "slug": "foundation-piece",
        "name": "Foundation Piece — Numbered",
        "short": "001/100. Awarded to founders only.",
        "category": "coin",
        "price": 0.0,
        "is_award_only": True,
        "images": ["/aegis/legacy-badge.jpg"],
        "accent": "#D4AF37",
        "sizes": ["1.75in"],
        "colors": [],
        "badge": "EARNED",
        "description": "The Foundation Piece. Numbered 1–100. Awarded only to the people who built the Order from the ground up. Antique gold finish, AEGIS LEGACY crest, individually serialized on the rim.",
    },
    {
        "slug": "legacy-patch-foundation",
        "name": "AEGIS Legacy Patch",
        "short": "Velcro-back. Awarded to the Order.",
        "category": "patch",
        "price": 0.0,
        "is_award_only": True,
        "images": ["/aegis/legacy-badge.jpg"],
        "accent": "#D4AF37",
        "sizes": ["3in"],
        "colors": [],
        "badge": "EARNED",
        "description": "The AEGIS LEGACY crest, rendered in full-bleed embroidery on velcro backing. Awarded — never sold — to founders, leaders, and contributors who built the Order.",
    },
    {
        "slug": "legacy-sticker-aegis",
        "name": "AEGIS Legacy Sticker",
        "short": "Numbered run. Hand-distributed.",
        "category": "sticker",
        "price": 0.0,
        "is_award_only": True,
        "images": ["/aegis/legacy-badge.jpg"],
        "accent": "#D4AF37",
        "sizes": ["3in"],
        "colors": [],
        "badge": "EARNED",
        "description": "Numbered LEGACY sticker run. Hand-distributed at unit ceremonies and milestone moments. If you have one, you earned it.",
    },
    {
        "slug": "legacy-sticker-core",
        "name": "AEGIS Core Sticker",
        "short": "CORE crest. The Standard.",
        "category": "sticker",
        "price": 0.0,
        "is_award_only": True,
        "images": ["/aegis/core-badge.jpg"],
        "accent": "#6B9DD3",
        "sizes": ["3in"],
        "colors": [],
        "badge": "EARNED",
        "description": "The CORE crest in sticker form. Awarded for sustained commitment to the standard. Not for sale.",
    },
    {
        "slug": "legacy-patch-order",
        "name": "AEGIS Order Patch",
        "short": "Merit patch. Awarded only.",
        "category": "patch",
        "price": 0.0,
        "is_award_only": True,
        "images": ["/aegis/legacy-badge.jpg"],
        "accent": "#D4AF37",
        "sizes": ["3in"],
        "colors": [],
        "badge": "EARNED",
        "description": "The Order patch. Awarded to those who uphold the standard in silence and in sight. Never sold, only granted.",
    },
]

CAMPAIGNS_RAW = [
    {
        "code": "001",
        "slug": "a-yard",
        "name": "A-YARD",
        "status": "active",
        "tagline": "Mule Creek State Prison. Five Buildings. One Mission.",
        "accent": "#D4AF37",
        "image": "/aegis/a-yard-badge.jpg",
        "bullets": [
            "Level IV high-security yard",
            "Code 2 / Code 3 operational tempo",
            "Built on discipline. United as one.",
        ],
        "description": "Where it started. A Yard at Mule Creek State Prison — California Level IV. The campaign that birthed the Order. The Dumpster Fire Response Team patch, the original A-Yard sticker, the AEGIS Foundation Piece — all trace their lineage here. Five buildings. One mission.",
    },
    {
        "code": "002",
        "slug": "eop",
        "name": "EOP",
        "status": "active",
        "tagline": "Mental Tough. Physical Tough. Mission Ready.",
        "accent": "#A23E48",
        "image": "/aegis/eop-badge.jpg",
        "bullets": [
            "Enhanced Outpatient Program operations",
            "Mental Health Team integration",
            "Clinicians + Custody as one unit",
        ],
        "description": "The Enhanced Outpatient Program campaign. Where Mental Health clinicians and Custody work together as one fighting unit. Strength in mind. Support in action. Awarded gear acknowledges the people who walked these floors on the toughest days.",
    },
    {
        "code": "003",
        "slug": "building-5",
        "name": "BUILDING 5",
        "status": "active",
        "tagline": "The Standard. Lives Here.",
        "accent": "#2F855A",
        "image": "/aegis/building-5-badge.jpg",
        "bullets": [
            "Highest standard on the yard",
            "Tier I custody operations",
            "The bar everyone else is measured against",
        ],
        "description": "Building 5. The standard. The bar. Where discipline, presence, and control are not slogans — they are baseline. The Building 5 campaign honors the watch that sets the tone for everything else on the yard.",
    },
    {
        "code": "004",
        "slug": "locked",
        "name": "LOCKED",
        "status": "coming_soon",
        "tagline": "Earn it. Unlock it. Live it.",
        "accent": "#8C92A0",
        "image": "/aegis/legacy-badge.jpg",
        "bullets": [],
        "description": "Campaign locked. Eligibility criteria forthcoming. This dossier becomes available when the conditions are met.",
    },
    {
        "code": "005",
        "slug": "classified",
        "name": "CLASSIFIED",
        "status": "classified",
        "tagline": "The next chapter awaits.",
        "accent": "#8C92A0",
        "image": "/aegis/core-badge.jpg",
        "bullets": [],
        "description": "Classified. Information regarding this campaign has been redacted at this time.",
    },
]

# Demo redeem codes (user can edit/replace via DB later)
LEGACY_REDEEM_CODES = {
    "AEGIS-FOUNDER-001": {
        "label": "AEGIS Founders Cohort",
        "unlocks": [
            "foundation-piece",
            "legacy-patch-foundation",
            "legacy-sticker-aegis",
        ],
    },
    "CORE-STANDARD-001": {
        "label": "Core Standard Bearer",
        "unlocks": [
            "legacy-sticker-core",
        ],
    },
    "FOUNDATION-001": {
        "label": "Foundation Piece Holder",
        "unlocks": ["foundation-piece"],
    },
    "BUILT-ON-DISCIPLINE": {
        "label": "Order Admin Override",
        "unlocks": [
            "foundation-piece",
            "legacy-patch-foundation",
            "legacy-sticker-aegis",
            "legacy-sticker-core",
            "legacy-patch-order",
        ],
    },
}

ORDER_SHIPPING_FEE = 7.99


def build_seed_products() -> List[Product]:
    out: List[Product] = []
    for raw in CORE_PRODUCTS_RAW:
        out.append(Product(division="core", **raw))
    for raw in LEGACY_PRODUCTS_RAW:
        out.append(Product(division="legacy", **raw))
    return out


def calculate_order_total(items: List[dict]) -> float:
    subtotal = 0.0
    for item in items:
        subtotal += float(item["price"]) * int(item["quantity"])
    return round(subtotal + ORDER_SHIPPING_FEE, 2)


async def get_order_product_items(items: List[OrderItemIn]) -> List[dict]:
    product_ids = [item.product_id for item in items]
    docs = await db.products.find({"id": {"$in": product_ids}}, {"_id": 0}).to_list(100)
    by_id = {doc["id"]: doc for doc in docs}
    resolved: List[dict] = []
    for item in items:
        product = by_id.get(item.product_id)
        if not product:
            raise HTTPException(400, f"Unknown product: {item.product_id}")
        if product.get("is_award_only"):
            raise HTTPException(400, "award-only products cannot be purchased")
        resolved.append({
            "product_id": product["id"],
            "slug": product["slug"],
            "name": product["name"],
            "price": product["price"],
            "quantity": max(1, int(item.quantity)),
            "size": item.size or "",
            "color": item.color or "",
        })
    return resolved


def normalize_origin_url(origin_url: str) -> str:
    return origin_url.rstrip("/")


@app.on_event("startup")
async def seed_data():
    meta = await db.meta.find_one({"key": "seed_version"})
    current = meta.get("value") if meta else None
    if current != SEED_VERSION:
        await db.products.delete_many({})
        await db.campaigns.delete_many({})
        prods = [p.model_dump() for p in build_seed_products()]
        await db.products.insert_many(prods)
        campaigns = [Campaign(**c).model_dump() for c in CAMPAIGNS_RAW]
        await db.campaigns.insert_many(campaigns)
        await db.meta.update_one(
            {"key": "seed_version"},
            {"$set": {"value": SEED_VERSION, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        logging.info(f"Re-seeded AEGIS data ({len(prods)} products, {len(campaigns)} campaigns)")


# ---------- ROUTES ----------
@api_router.get("/")
async def root():
    return {"message": "AEGIS — Strength in Order", "status": "operational"}


@api_router.get("/products", response_model=List[Product])
async def list_products(
    category: Optional[str] = None,
    division: Optional[str] = None,
    featured: Optional[bool] = None,
):
    q: Dict = {}
    if category:
        q["category"] = category
    if division:
        q["division"] = division
    if featured is not None:
        q["featured"] = featured
    docs = await db.products.find(q, {"_id": 0}).to_list(500)
    return docs


@api_router.get("/products/filters")
async def product_filters():
    cats = await db.products.distinct("category")
    divisions = await db.products.distinct("division")
    return {"categories": cats, "divisions": divisions}


@api_router.get("/products/{slug}", response_model=Product)
async def get_product(slug: str):
    doc = await db.products.find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Product not found")
    return doc


@api_router.get("/campaigns", response_model=List[Campaign])
async def list_campaigns():
    docs = await db.campaigns.find({}, {"_id": 0}).sort("code", 1).to_list(50)
    return docs


@api_router.get("/campaigns/{slug}", response_model=Campaign)
async def get_campaign(slug: str):
    doc = await db.campaigns.find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Campaign not found")
    return doc


# ---------- LEGACY REDEEM / REQUEST ----------
@api_router.post("/legacy/redeem")
async def redeem_legacy(payload: RedeemIn):
    code = payload.code.strip().upper()
    entry = LEGACY_REDEEM_CODES.get(code)
    if not entry:
        raise HTTPException(400, "Invalid code. Codes are case-insensitive but must match exactly.")
    # Find product ids by slug
    slugs = entry["unlocks"]
    docs = await db.products.find({"slug": {"$in": slugs}}, {"_id": 0, "id": 1, "slug": 1, "name": 1}).to_list(50)
    return {
        "label": entry["label"],
        "unlocked_product_ids": [d["id"] for d in docs],
        "unlocked_slugs": [d["slug"] for d in docs],
        "unlocked_names": [d["name"] for d in docs],
    }


@api_router.post("/legacy/request")
async def legacy_request(payload: LegacyRequestIn):
    rec = {
        "id": str(uuid.uuid4()),
        "full_name": payload.full_name,
        "email": payload.email,
        "unit": payload.unit,
        "story": payload.story,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.legacy_requests.insert_one(rec)
    return {"ok": True, "id": rec["id"]}


# ---------- ORDERS / CHECKOUT ----------
@api_router.post("/orders/manual")
async def create_manual_order(payload: ManualOrderIn):
    items = await get_order_product_items(payload.items)
    order_id = str(uuid.uuid4())
    total = calculate_order_total(items)
    rec = {
        "id": order_id,
        "order_type": "manual",
        "payment_status": "awaiting_manual",
        "items": items,
        "customer": {
            "name": payload.customer_name,
            "email": payload.customer_email,
            "address_line1": payload.address_line1,
            "address_line2": payload.address_line2 or "",
            "city": payload.city,
            "state": payload.state,
            "zip_code": payload.zip_code,
        },
        "notes": payload.notes or "",
        "origin_url": payload.origin_url,
        "total": total,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.orders.insert_one(rec)
    return {
        "ok": True,
        "order_id": order_id,
        "total": total,
        "payment_status": rec["payment_status"],
    }


@api_router.get("/orders/{order_id}")
async def get_order(order_id: str):
    doc = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Order not found")
    return doc


@api_router.post("/checkout/session")
async def create_checkout_session(payload: CheckoutSessionIn):
    items = await get_order_product_items(payload.items)
    order_id = str(uuid.uuid4())
    total = calculate_order_total(items)
    rec = {
        "id": order_id,
        "order_type": "checkout",
        "payment_status": "pending_checkout",
        "items": items,
        "customer": {
            "name": payload.customer_name,
            "email": payload.customer_email,
            "address_line1": payload.address_line1,
            "address_line2": payload.address_line2 or "",
            "city": payload.city,
            "state": payload.state,
            "zip_code": payload.zip_code,
        },
        "notes": payload.notes or "",
        "origin_url": payload.origin_url,
        "total": total,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.orders.insert_one(rec)
    redirect_base = normalize_origin_url(payload.origin_url)
    return {
        "session_id": order_id,
        "url": f"{redirect_base}/success?session_id={order_id}",
        "total": total,
    }


# ---------- NEWSLETTER / CONTACT ----------
class NewsletterIn(BaseModel):
    email: str


@api_router.post("/newsletter")
async def subscribe(payload: NewsletterIn):
    await db.newsletter.insert_one({
        "id": str(uuid.uuid4()),
        "email": payload.email,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True}


@api_router.post("/contact")
async def contact(payload: ContactIn):
    rec = {
        "id": str(uuid.uuid4()),
        "full_name": payload.full_name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.contact_messages.insert_one(rec)
    return {"ok": True, "id": rec["id"]}


# ---------- APP WIRING ----------
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves the built React app (see Dockerfile) so the API and frontend
# can run as a single deployed service.
FRONTEND_BUILD_DIR = ROOT_DIR / "build"
if FRONTEND_BUILD_DIR.is_dir():
    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        candidate = FRONTEND_BUILD_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
