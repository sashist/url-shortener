import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).parent.parent))

from src.api.links import redirect_router
from src.api.router import api_router
from src.init import rabbit_manager, redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    await rabbit_manager.connect()

    yield

    await redis_manager.close()
    await rabbit_manager.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)
app.include_router(api_router)
app.include_router(redirect_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
