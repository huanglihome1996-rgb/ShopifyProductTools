"""
测试配置和工具
"""
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.database import Base, get_db
from src.app import app


# 测试数据库 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试 HTTP 客户端"""
    from httpx import ASGITransport
    
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_store(test_session: AsyncSession):
    """创建示例店铺"""
    from src.models import Store
    from src.utils.crypto import encrypt_token
    
    store = Store(
        name="测试店铺",
        shop_url="test-store.myshopify.com",
        access_token=encrypt_token("test_token_123"),
        is_active=True,
    )
    test_session.add(store)
    await test_session.commit()
    await test_session.refresh(store)
    return store


@pytest.fixture
async def sample_product(test_session: AsyncSession, sample_store):
    """创建示例产品"""
    from src.models import Product
    
    product = Product(
        store_id=sample_store.id,
        sku="TEST-001",
        original_title="测试产品标题",
        original_description="这是一个测试产品的描述",
        original_price=99.99,
        source_type="excel",
        status="pending",
        is_draft=True,
    )
    test_session.add(product)
    await test_session.commit()
    await test_session.refresh(product)
    return product