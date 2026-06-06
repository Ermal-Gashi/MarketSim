import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.routes.simulate import router as simulate_router

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="MarketSim")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
