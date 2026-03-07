from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.extended_analytics import router as extended_analytics_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.orders import router as orders_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.retell_integration import router as retell_integration_router
from app.api.v1.voice import router as voice_router


api_router = APIRouter()
api_router.include_router(ingestion_router)
api_router.include_router(analytics_router)
api_router.include_router(recommendations_router)
api_router.include_router(dashboard_router)
api_router.include_router(voice_router)
api_router.include_router(orders_router)
api_router.include_router(extended_analytics_router)
api_router.include_router(retell_integration_router)
