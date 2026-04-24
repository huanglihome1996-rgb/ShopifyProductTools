"""
产品 API 测试
"""
import pytest
from httpx import AsyncClient


class TestProductAPI:
    """产品 API 测试类"""

    @pytest.mark.asyncio
    async def test_list_products_empty(self, client: AsyncClient):
        """测试空产品列表"""
        response = await client.get("/api/products/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_create_product(self, client: AsyncClient, sample_store):
        """测试创建产品"""
        data = {
            "store_id": sample_store.id,
            "sku": "NEW-001",
            "original_title": "新产品标题",
            "original_description": "新产品描述",
            "original_price": 199.99,
            "source_type": "manual",
        }
        response = await client.post("/api/products/", json=data)
        assert response.status_code == 201
        
        product = response.json()
        assert product["sku"] == "NEW-001"
        assert product["original_title"] == "新产品标题"
        assert product["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_products_with_data(self, client: AsyncClient, sample_product):
        """测试有数据的产品列表"""
        response = await client.get("/api/products/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["sku"] == "TEST-001"

    @pytest.mark.asyncio
    async def test_list_products_filter_by_store(
        self, client: AsyncClient, sample_product, sample_store
    ):
        """测试按店铺筛选产品"""
        response = await client.get(f"/api/products/?store_id={sample_store.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_products_filter_by_status(
        self, client: AsyncClient, sample_product
    ):
        """测试按状态筛选产品"""
        response = await client.get("/api/products/?status=pending")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_products_search(self, client: AsyncClient, sample_product):
        """测试搜索产品"""
        response = await client.get("/api/products/?search=测试")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_get_product(self, client: AsyncClient, sample_product):
        """测试获取单个产品"""
        response = await client.get(f"/api/products/{sample_product.id}")
        assert response.status_code == 200
        
        product = response.json()
        assert product["sku"] == "TEST-001"
        assert product["original_title"] == "测试产品标题"

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, client: AsyncClient):
        """测试获取不存在的产品"""
        response = await client.get("/api/products/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_product_by_sku(self, client: AsyncClient, sample_product, sample_store):
        """测试通过 SKU 获取产品"""
        response = await client.get(
            f"/api/products/sku/{sample_product.sku}?store_id={sample_store.id}"
        )
        assert response.status_code == 200
        
        product = response.json()
        assert product["sku"] == "TEST-001"

    @pytest.mark.asyncio
    async def test_delete_product(self, client: AsyncClient, sample_product):
        """测试删除产品"""
        response = await client.delete(f"/api/products/{sample_product.id}")
        assert response.status_code == 200
        
        # 验证已删除
        response = await client.get(f"/api/products/{sample_product.id}")
        assert response.status_code == 404
