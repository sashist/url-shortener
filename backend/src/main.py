import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).parent.parent))

from src.api.links import redirect_router
from src.api.router import api_router
from src.core.logging import logger, setup_logging
from src.init import rabbit_manager, redis_manager

setup_logging()



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up URL Shortener backend...")

    await redis_manager.connect()
    logger.info("Connected to Redis Cache")

    await rabbit_manager.connect()
    logger.info(" Connected to RabbitMQ Broker (Exchange & Queue bound)")

    yield

    logger.info("Shutting down URL Shortener backend...")

    await redis_manager.close()
    logger.info("Redis connection closed")

    await rabbit_manager.close()
    logger.info("RabbitMQ connection closed")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.bind(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
    ).info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)"
    )

    return response


app.include_router(api_router)
app.include_router(redirect_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
