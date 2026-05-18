import app.models_registry

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.common.exceptions import register_exception_handlers

from app.auth.routes import router as auth_router
from app.users.users.routes import router as users_router

from app.geo.countries.routers import router as countries_router
from app.geo.cities.routers import router as cities_router

from app.requests.requests.routes import router as requests_router
from app.requests.request_items.routes import router as request_items_router
from app.requests.request_offers.routes import router as request_offers_router
from app.requests.request_item_assignment.routes import router as request_item_assignment_router
from app.requests.request_images.routes import router as request_images_router

from app.notifications.notifications.routes import router as notifications_router

from app.consents.routes import router as consents_router

from app.chats.chats.routers import router as chats_router
from app.chats.messages.routers import router as messages_router
from app.chats.managing.routers import router as ws_chat_router

from app.reviews.routes import router as review_router

from app.ws.routes import router as ws_notifications_router


app = FastAPI(title="VolonterUA")
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для тесту
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(auth_router)

app.include_router(users_router)

app.include_router(countries_router)
app.include_router(cities_router)

app.include_router(requests_router)
app.include_router(request_items_router)
app.include_router(request_offers_router)
app.include_router(request_item_assignment_router)
app.include_router(request_images_router)

app.include_router(notifications_router)
app.include_router(ws_notifications_router)

app.include_router(consents_router)

app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(ws_chat_router)

app.include_router(review_router)


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.on_event("startup")
async def startup():
    import asyncio
    from app.ws.redis_listener import redis_listener

    asyncio.create_task(redis_listener())
