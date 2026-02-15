import os

PORT = int(os.environ.get("PORT", 8000))
from fastapi import FastAPI
import time
import hashlib

app = FastAPI()

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
def chatbot(data: dict):

    stats["total"] += 1

    query = clean(data["query"])
    key = make_key(query)

    start = time.time()

    # Check cache
    if key in cache:
        stats["hits"] += 1

        return {
            "answer": cache[key],
            "cached": True,
            "latency": int((time.time()-start)*1000),
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
