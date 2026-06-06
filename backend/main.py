import logging
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="MarketSim")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
