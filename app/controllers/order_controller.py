from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order_schemas import OrderCreateSchema


async def create_order_logic(
    session: AsyncSession, user_id: int, data: OrderCreateSchema
) -> Order:
    """
    1) Yangi order yaratish (flush / commit),
    2) total_price hisoblash,
    3) order_itemsni create qilish,
    4) yakunda selectinload(Order.items) bilan orderni qayta so'rab, to'liq obyektni qaytarish
    """

    # 1) Yangi order
    new_order = Order(user_id=user_id, total_price=0.0, status="pending")
    session.add(new_order)
    # flush => new_order.id hosil bo'ladi
    await session.flush()

    total_price = 0.0

    # 2) Har bir item uchun
    for item in data.items:
        product = await session.scalar(
            select(Product).where(Product.id == item.product_id)
        )
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient quantity for product {item.product_id}",
            )

        # Update product quantity
        product.quantity -= item.quantity
        total_price += item.quantity * product.price
        session.add(product)
        # OrderItem
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price,
        )
        session.add(order_item)

    new_order.total_price = total_price
    await session.flush()

    # 4) endi commit
    await session.commit()

    # 5) commit bo'lgach, orderni selectinload bilan qaytadan olib kelamiz
    result_order = await session.scalar(
        select(Order).options(selectinload(Order.items)).where(Order.id == new_order.id)
    )
    # result_order.items -> allaqachon yuklangan bo'ladi

    return result_order


async def get_order_logic(
    session: AsyncSession, current_user: User, order_id: int
) -> Order:
    """
    Bitta orderni oldindan order.items ni ham eager load qilgan holda yuklash
    """
    order = await session.scalar(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Ruxsat
    if (not current_user.is_superuser) and (order.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden")

    return order


async def get_all_orders_logic(
    session: AsyncSession, admin_user: User
) -> Sequence[Order]:
    """
    Admin barcha orderlarni ko‘ra oladi
    """
    if not admin_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Hammasini selectinload bilan yuklash
    orders = await session.scalars(select(Order).options(selectinload(Order.items)))
    # .all() -> list[Order]
    return orders.all()


async def get_customer_orders_logic(
    session: AsyncSession, current_user: User, customer_id: int
) -> Sequence[Order]:
    """
    Customer faqat o‘ziga tegishli orderlarini ko‘rishi mumkin,
    Admin esa xohlagan customerning orderlarini ko‘ra oladi.
    """
    if (not current_user.is_superuser) and (current_user.id != customer_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    orders = await session.scalars(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == customer_id)
    )
    return orders.all()


async def get_order_status_logic(
    session: AsyncSession, current_user: User, order_id: int
) -> dict:
    """
    Faqat statusni qaytarish
    """
    order = await session.scalar(select(Order).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if (not current_user.is_superuser) and (order.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"status": order.status}
