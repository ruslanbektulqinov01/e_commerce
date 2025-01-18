from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db import get_async_session
from app.models.user import User
from app.schemas.product_schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductOutSchema,
)
from app.services.security import get_current_user
from app.controllers.product_controller import (
    create_product_logic,
    update_product_logic,
    delete_product_logic,
)
from sqlalchemy import select

products_router = APIRouter(prefix="/products", tags=["Products"])


@products_router.get("/", response_model=List[ProductOutSchema])
async def get_products(session: AsyncSession = Depends(get_async_session)):
    from app.models.product import Product

    products = (
        await session.scalars(select(Product).where(Product.is_active == True))
    ).all()
    return products


@products_router.post("/", response_model=ProductOutSchema)
async def create_product(
    product_data: ProductCreateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user = (
        await session.scalars(select(User).where(User.email == current_user_email))
    ).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden (admin only)")

    return await create_product_logic(session, product_data)


@products_router.get("/{product_id}", response_model=ProductOutSchema)
async def get_product(
    product_id: int, session: AsyncSession = Depends(get_async_session)
):
    from app.models.product import Product

    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@products_router.put("/{product_id}", response_model=ProductOutSchema)
async def update_product(
    product_id: int,
    product_data: ProductUpdateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user = (
        await session.scalars(select(User).where(User.email == current_user_email))
    ).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden (admin only)")

    return await update_product_logic(session, product_id, product_data)


@products_router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user = (
        await session.scalars(select(User).where(User.email == current_user_email))
    ).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden (admin only)")

    return await delete_product_logic(session, product_id)
