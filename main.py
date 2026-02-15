import os

PORT = int(os.environ.get("PORT", 8000))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import hashlib

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple cache
cache = {}
stats = {
    "total": 0,
    "hits": 0,
    "misses": 0
}

# Normalize text
def clean(text):
    return text.strip().lower()

# Create hash
def make_key(text):
    return hashlib.md5(text.encode()).hexdigest()

@app.post("/")
def chatbot(request: dict):
    start = time.time()

    query = request.get("query", "").lower().strip()

    if not query:
        latency = max(1, int((time.time() - start) * 1000))
        return {
            "answer": "Empty query",
            "cached": False,
            "latency": latency,
            "cacheKey": "none"
        }

    key = hashlib.md5(query.encode()).hexdigest()

    # Cache hit
    if key in cache:
        latency = max(1, int((time.time() - start) * 1000))
        return {
            "answer": cache[key],
            "cached": True,
            "latency": latency,
            "cacheKey": key
        }

    # Cache miss
    answer = f"This is AI answer for: {query}"
    cache[key] = answer

    latency = max(1, int((time.time() - start) * 1000))

    return {
        "answer": answer,
        "cached": False,
        "latency": latency,
        "cacheKey": key
    }


    # Cache miss → fake AI
    stats["misses"] += 1

    answer = "This is AI answer for: " + query

    cache[key] = answer

    return {
        "answer": answer,
        "cached": False,
        "latency": int((time.time()-start)*1000),
        "cacheKey": key
    }


@app.get("/analytics")
def analytics():

    hit_rate = 0
    if stats["total"] > 0:
        hit_rate = stats["hits"] / stats["total"]

    return {
        "hitRate": round(hit_rate,2),
        "totalRequests": stats["total"],
        "cacheHits": stats["hits"],
        "cacheMisses": stats["misses"],
        "cacheSize": len(cache),
        "strategies": [
            "exact match",
            "normalization",
            "basic caching"
        ]
    }
@app.get("/")
def home():
    return {
        "answer": "AI Cache API is running",
        "cached": True,
        "latency": 1,
        "cacheKey": "system"
    }

