from fastapi import APIRouter

from .routers.counts import router as counts_router
from .routers.customers import router as customers_router

api_router = APIRouter()
api_router.include_router(counts_router)    # static routes first (e.g. /customers/count)
api_router.include_router(customers_router) # dynamic routes second (e.g. /customers/{id})
