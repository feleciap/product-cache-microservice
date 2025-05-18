from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Product


async def fetch_product(product_id: int, db:AsyncSession):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalars().first()

    if product:
        return {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "description": product.description,
        }
    return None