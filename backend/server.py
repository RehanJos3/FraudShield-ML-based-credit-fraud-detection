from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
from backend.fraud_api import fraud_router


ROOT_DIR = Path(__file__).parent
# Load env from backend/.env if present
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (optional for basic API functionality)
client = None
db = None
try:
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'fraudshield')
    if mongo_url:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
except Exception:
    client = None
    db = None

# Create the main app without a prefix
app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="Production-ready fraud detection system with machine learning",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {
        "message": "Credit Card Fraud Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "fraud_detection": "/api/fraud/",
            "health_check": "/api/fraud/health",
            "dataset_info": "/api/fraud/dataset/info"
        }
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    if db is None:
        # Fallback to echo without persistence when DB is not configured
        return StatusCheck(client_name=input.client_name)
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if db is None:
        return []
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include routers in the main app
app.include_router(api_router)
app.include_router(fraud_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()
