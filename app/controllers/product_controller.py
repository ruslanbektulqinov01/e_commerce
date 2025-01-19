from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product_schemas import ProductCreateSchema, ProductUpdateSchema


async def create_product_logic(
    session: AsyncSession, data: ProductCreateSchema
) -> Product:
    # Masalan, name dublikat bo‘lmasin:
    existing = await session.scalar(select(Product).where(Product.name == data.name))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists",
        )
    new_product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        quantity=data.quantity,
        is_active=data.is_active,
    )
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product


async def update_product_logic(
    session: AsyncSession, product_id: int, data: ProductUpdateSchema
) -> Product:
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.name is not None:
        product.name = data.name
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.is_active is not None:
        product.quantity = data.quantity

    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def delete_product_logic(session: AsyncSession, product_id: int):
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await session.delete(product)
    await session.commit()
    return {"message": "Product deleted successfully"}
