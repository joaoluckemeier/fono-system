from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.config import get_settings
from backend.infrastructure.observability.logging import configurar_logging
from backend.interface.middlewares.audit import AuditMiddleware
from backend.interface.middlewares.correlation_id import CorrelationIdMiddleware
from backend.interface.middlewares.rate_limit import limiter, rate_limit_exceeded_handler
from backend.interface.routers.anexos_router import router as anexos_router
from backend.interface.routers.auth_router import router as auth_router
from backend.interface.routers.caa_router import router as caa_router
from backend.interface.routers.evolucoes_router import router as evolucoes_router
from backend.interface.routers.pacientes_router import router as pacientes_router
from backend.interface.routers.profissionais_router import router as profissionais_router
from backend.interface.routers.protocolos_router import router as protocolos_router

settings = get_settings()
configurar_logging(settings.environment)

app = FastAPI(title="Fono System")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(profissionais_router)
app.include_router(protocolos_router)
app.include_router(caa_router)
app.include_router(evolucoes_router)
app.include_router(anexos_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
