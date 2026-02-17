import os
import json
import redis
import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, generate_latest
from starlette.responses import Response

app = FastAPI(title="User Service")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE", "http://product-service")
ORDER_SERVICE = os.getenv("ORDER_SERVICE", "http://order-service")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

REQUEST_COUNT = Counter("user_requests_total", "Total user requests")

@app.on_event("startup")
def init_data():
    if not r.exists("user:1"):
        for i in range(1, 11):
            user = {
                "id": i,
                "name": f"User-{i}",
                "email": f"user{i}@mail.com"
            }
            r.set(f"user:{i}", json.dumps(user))

@app.get("")
@app.get("/")
def index():
    return {"message": "Hello from User Service!"}

@app.get("/users")
@app.get("/users/")
def get_users():
    REQUEST_COUNT.inc()
    return [json.loads(r.get(k)) for k in r.keys("user:*")]

@app.get("/users/{user_id}")
@app.get("/users/{user_id}/")
def get_user(user_id: int):
    REQUEST_COUNT.inc()
    data = r.get(f"user:{user_id}")
    if not data:
        raise HTTPException(404)
    return json.loads(data)

# 🔁 Call Order Service
@app.get("/users/{user_id}/orders")
@app.get("/users/{user_id}/orders/")
async def get_user_orders(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ORDER_SERVICE}/orders/by-user/{user_id}")
        return resp.json()

# 🔁 Call Product Service
@app.get("/users/{user_id}/recommendations")
@app.get("/users/{user_id}/recommendations/")
async def recommend_products(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PRODUCT_SERVICE}/products")
        return resp.json()[:3]

@app.get("/metrics")
@app.get("/metrics/")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/health")
@app.get("/health/")
def health():
    return {"status": "ok"}