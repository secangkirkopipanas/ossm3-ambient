import os
import json
import redis
import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI(title="Product Service")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
USER_SERVICE = os.getenv("USER_SERVICE", "http://user-service")
ORDER_SERVICE = os.getenv("ORDER_SERVICE", "http://order-service")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

REQUEST_COUNT = Counter("product_requests_total", "Total product requests")
REQUEST_LATENCY = Histogram("product_request_latency_seconds", "Request latency")

@app.on_event("startup")
def init_data():
    if not r.exists("product:1"):
        for i in range(1, 11):
            product = {
                "id": i,
                "name": f"Product-{i}",
                "price": 10 * i,
                "stock": 100
            }
            r.set(f"product:{i}", json.dumps(product))

@app.get("")
@app.get("/")
def index():
    return {"message": "Hello from Product Service!"}

@app.get("/products")
@app.get("/products/")
def get_products():
    REQUEST_COUNT.inc()
    products = []
    for key in r.keys("product:*"):
        products.append(json.loads(r.get(key)))
    return products

@app.get("/products/{product_id}")
@app.get("/products/{product_id}/")
def get_product(product_id: int):
    REQUEST_COUNT.inc()
    data = r.get(f"product:{product_id}")
    if not data:
        raise HTTPException(404)
    return json.loads(data)

# 🔁 Call User Service
@app.get("/products/{product_id}/buyers")
@app.get("/products/{product_id}/buyers/")
async def get_buyers(product_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ORDER_SERVICE}/orders/by-product/{product_id}")
        return resp.json()

# 🔁 Call Order Service
@app.get("/products/{product_id}/orders/count")
@app.get("/products/{product_id}/orders/count/")
async def get_order_count(product_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ORDER_SERVICE}/orders/count/{product_id}")
        return resp.json()

@app.get("/metrics")
@app.get("/metrics/")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/health")
@app.get("/health/")
def health():
    return {"status": "ok"}