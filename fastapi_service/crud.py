from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from .models import Product
from .settings import settings


DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

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