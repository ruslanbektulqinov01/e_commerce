from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db import get_async_session
from app.models.product import Product
from app.models.user import User
from app.schemas.product_schemas import (
    ProductCreateSchema, ProductUpdateSchema, ProductOutSchema
)
from app.services.security import get_current_user

products_router = APIRouter(prefix="/api/products", tags=["Products"])

@products_router.get("/", response_model=List[ProductOutSchema])
async def get_products(session: AsyncSession = Depends(get_async_session)):
    products = (await session.scalars(select(Product).where(Product.is_active == True))).all()
    return products

@products_router.post("/", response_model=ProductOutSchema)
async def create_product(
    product_data: ProductCreateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Admin check using ORM
    user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden (admin only)")

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        is_active=product_data.is_active
    )
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product

@products_router.get("/{product_id}", response_model=ProductOutSchema)
async def get_product(product_id: int, session: AsyncSession = Depends(get_async_session)):
    product = await session.scalar(
        select(Product).where(Product.id == product_id)
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@products_router.put("/{product_id}", response_model=ProductOutSchema)
async def update_product(
    product_id: int,
    product_data: ProductUpdateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Admin check using ORM
    user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden (admin only)")

    # Find product using ORM
    product = await session.scalar(
        select(Product).where(Product.id == product_id)
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update product fields if provided
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.is_active is not None:
        product.is_active = product_data.is_active

    await session.commit()
    await session.refresh(product)
    return product

@products_router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Admin check using ORM
    user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden (admin only)")

    # Find product using ORM
    product = await session.scalar(
        select(Product).where(Product.id == product_id)
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await session.delete(product)
    await session.commit()
    return {"message": "Product deleted successfully"}