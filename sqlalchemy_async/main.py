import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from models import Base, User


# ✅ 数据库配置
DSN = "postgresql+asyncpg://postgres:changethis@47.254.42.5:5432/brain_x"

# ✅ 创建异步引擎
engine = create_async_engine(DSN, echo=True)

# ✅ 创建异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# ✅ 初始化数据库（建表）
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ✅ 示例操作：插入用户 + 查询用户
async def create_and_query_user():
    async with AsyncSessionLocal() as session:
        # 插入新用户
        new_user = User(name="Alice")
        session.add(new_user)
        await session.commit()

        # 查询所有用户
        result = await session.execute(select(User))
        users = result.scalars().all()
        print("Users in DB:", users)


# ✅ 程序入口
async def main():
    await init_db()
    await create_and_query_user()


if __name__ == "__main__":
    asyncio.run(main())