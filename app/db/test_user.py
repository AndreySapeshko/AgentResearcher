import asyncio

from sqlalchemy import select

from app.db.models import User
from app.db.session import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as session:
        # create
        user = User(telegram_id=123456789, username="test_user")
        session.add(user)
        await session.commit()

        # read
        stmt = select(User).where(User.telegram_id == 123456789)
        result = await session.execute(stmt)
        db_user = result.scalar_one()

        print(db_user)


if __name__ == "__main__":
    asyncio.run(main())
