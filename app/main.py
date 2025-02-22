from fastapi import FastAPI
from app.routers.auth import auth_router
from app.routers.users import users_router
from app.routers.products import products_router
from app.routers.orders import orders_router
from app.db import engine, Base

app = FastAPI(title="E-commerce")

# Routerlarni ulash
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(orders_router)


@app.get("/")
async def root():
    return {"message": "Welcome, my e-commerce platform!"}
