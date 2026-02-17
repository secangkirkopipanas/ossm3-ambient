import os
import json
import redis
import random
import httpx
from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from starlette.responses import Response

app = FastAPI(title="Order Service")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
USER_SERVICE = os.getenv("USER_SERVICE", "http://user-service")
PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE", "http://product-service")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

REQUEST_COUNT = Counter("order_requests_total", "Total order requests")

@app.on_event("startup")
def init_data():
    if not r.exists("order:1"):
        for i in range(1, 11):
            order = {
                "id": i,
                "user_id": random.randint(1, 10),
                "product_id": random.randint(1, 10),
                "quantity": random.randint(1, 5)
            }
            r.set(f"order:{i}", json.dumps(order))

@app.get("")
@app.get("/")
def index():
    return {"message": "Hello from Order Service!"}

@app.get("/orders")
@app.get("/orders/")
def get_orders():
    REQUEST_COUNT.inc()
    return [json.loads(r.get(k)) for k in r.keys("order:*")]

@app.get("/orders/by-user/{user_id}")
@app.get("/orders/by-user/{user_id}/")
def get_by_user(user_id: int):
    return [
        json.loads(r.get(k))
        for k in r.keys("order:*")
        if json.loads(r.get(k))["user_id"] == user_id
    ]

@app.get("/orders/by-product/{product_id}")
@app.get("/orders/by-product/{product_id}/")
def get_by_product(product_id: int):
    return [
        json.loads(r.get(k))
        for k in r.keys("order:*")
        if json.loads(r.get(k))["product_id"] == product_id
    ]

@app.get("/orders/count/{product_id}")
@app.get("/orders/count/{product_id}/")
def count_orders(product_id: int):
    count = len(get_by_product(product_id))
    return {"product_id": product_id, "count": count}

# 🔁 Call User Service
@app.get("/orders/{order_id}/user")
@app.get("/orders/{order_id}/user/")
async def get_order_user(order_id: int):
    order = json.loads(r.get(f"order:{order_id}"))
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE}/users/{order['user_id']}")
        return resp.json()

# 🔁 Call Product Service
@app.get("/orders/{order_id}/product")
@app.get("/orders/{order_id}/product/")
async def get_order_product(order_id: int):
    order = json.loads(r.get(f"order:{order_id}"))
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PRODUCT_SERVICE}/products/{order['product_id']}")
        return resp.json()

@app.get("/metrics")
@app.get("/metrics/")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/health")
@app.get("/health/")
def health():
    return {"status": "ok"}