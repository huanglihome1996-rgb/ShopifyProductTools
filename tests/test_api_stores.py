"""
店铺 API 测试
"""
import pytest
from httpx import AsyncClient


class TestStoreAPI:
    """店铺 API 测试类"""

    @pytest.mark.asyncio
    async def test_list_stores_empty(self, client: AsyncClient):
        """测试空店铺列表"""
        response = await client.get("/api/stores/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_store(self, client: AsyncClient):
        """测试创建店铺"""
        data = {
            "name": "新店铺",
            "shop_url": "new-store.myshopify.com",
            "access_token": "shpat_test_token",
        }
        response = await client.post("/api/stores/", json=data)
        assert response.status_code == 201
        
        result = response.json()
        assert result["name"] == "新店铺"
        assert result["shop_url"] == "new-store.myshopify.com"
        assert result["is_active"] is True
        assert "id" in result

    @pytest.mark.asyncio
    async def test_list_stores_with_data(self, client: AsyncClient, sample_store):
        """测试有数据的店铺列表"""
        response = await client.get("/api/stores/")
        assert response.status_code == 200
        
        stores = response.json()
        assert len(stores) == 1
        assert stores[0]["name"] == "测试店铺"

    @pytest.mark.asyncio
    async def test_get_store(self, client: AsyncClient, sample_store):
        """测试获取单个店铺"""
        response = await client.get(f"/api/stores/{sample_store.id}")
        assert response.status_code == 200
        
        store = response.json()
        assert store["name"] == "测试店铺"
        assert store["shop_url"] == "test-store.myshopify.com"

    @pytest.mark.asyncio
    async def test_get_store_not_found(self, client: AsyncClient):
        """测试获取不存在的店铺"""
        response = await client.get("/api/stores/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_store(self, client: AsyncClient, sample_store):
        """测试更新店铺"""
        data = {"name": "更新后的店铺"}
        response = await client.put(f"/api/stores/{sample_store.id}", json=data)
        assert response.status_code == 200
        
        store = response.json()
        assert store["name"] == "更新后的店铺"

    @pytest.mark.asyncio
    async def test_delete_store(self, client: AsyncClient, sample_store):
        """测试删除店铺"""
        response = await client.delete(f"/api/stores/{sample_store.id}")
        assert response.status_code == 200
        
        # 验证已删除
        response = await client.get(f"/api/stores/{sample_store.id}")
        assert response.status_code == 404
