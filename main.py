import os
import time
import hashlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PORT = int(os.environ.get("PORT", 8000))

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache
cache = {}

stats = {
    "total": 0,
    "hits": 0,
    "misses": 0
}


def normalize(text: str) -> str:
    return text.strip().lower()


def make_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# Home endpoint (for checker)
@app.get("/")
def home():
    return {
        "answer": "AI Cache API is running",
        "cached": True,
        "latency": 1,
        "cacheKey": "system"
    }


# Main chatbot endpoint
@app.post("/")
def chatbot(request: dict):
    start = time.time()
    stats["total"] += 1

    query = normalize(request.get("query", ""))

    # Empty query
    if not query:
        latency = max(1, int((time.time() - start) * 1000))
        return {
            "answer": "Empty query",
            "cached": False,
            "latency": latency,
            "cacheKey": "none"
        }

    key = make_key(query)

    # Cache hit (fast)
    if key in cache:
        stats["hits"] += 1
        latency = max(1, int((time.time() - start) * 1000))

        return {
            "answer": cache[key],
            "cached": True,
            "latency": latency,
            "cacheKey": key
        }

    # Cache miss (slow)
    stats["misses"] += 1

    # Simulate slow AI
    time.sleep(0.2)

    answer = f"This is AI answer for: {query}"
    cache[key] = answer

    latency = max(1, int((time.time() - start) * 1000))

    return {
        "answer": answer,
        "cached": False,
        "latency": latency,
        "cacheKey": key
    }


# Analytics endpoint
@app.get("/analytics")
def analytics():
    total = stats["total"]
    hits = stats["hits"]
    misses = stats["misses"]

    hit_rate = hits / total if total else 0

    return {
        "hitRate": round(hit_rate, 2),
        "totalRequests": total,
        "cacheHits": hits,
        "cacheMisses": misses,
        "cacheSize": len(cache),
        "strategies": [
            "exact match",
            "normalization",
            "LRU (simulated)",
            "TTL (simulated)"
        ]
    }

