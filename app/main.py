from fastapi import FastAPI
from app.routers.auth import auth_router
from app.routers.users import users_router
from app.routers.products import products_router
from app.routers.orders import orders_router

from app.db import engine, Base, USE_SQLITE_IN_MEMORY

app = FastAPI(title="Controller-based E-commerce")

# Routerlarni ulash
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(orders_router)


@app.on_event("startup")
async def startup_event():
    # Agar sqlite in-memory bo'lsa, dastur startida jadvallar yaratiladi
    if USE_SQLITE_IN_MEMORY:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI with Controllers!"}
