"""
Shopify API 客户端封装
"""
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx

from src.config import settings
from src.models import Store, Product
from src.utils.crypto import decrypt_token


class ShopifyClient:
    """Shopify API 客户端"""
    
    def __init__(self, store: Store):
        self.store = store
        self.access_token = decrypt_token(store.access_token)
        self.base_url = f"https://{store.shop_url}/admin/api/{settings.shopify_api_version}"
        self.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict:
        """发送 API 请求"""
        url = f"{self.base_url}/{endpoint}"
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
            )
            
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 429:
                # Rate limit
                raise Exception("Shopify API rate limit exceeded")
            elif response.status_code == 404:
                raise Exception("Resource not found")
            else:
                raise Exception(f"Shopify API error: {response.status_code} - {response.text}")
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            result = await self._request("GET", "shop.json")
            return "shop" in result
        except:
            return False
    
    async def get_product(self, product_id: str) -> Optional[Dict]:
        """获取单个产品"""
        try:
            result = await self._request("GET", f"products/{product_id}.json")
            return result.get("product")
        except:
            return None
    
    async def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        """通过 SKU 查找产品"""
        try:
            result = await self._request(
                "GET",
                "products.json",
                params={"handle": sku}
            )
            products = result.get("products", [])
            # 进一步匹配 SKU
            for product in products:
                for variant in product.get("variants", []):
                    if variant.get("sku") == sku:
                        return product
            return None
        except:
            return None
    
    async def create_product(self, product_data: Dict, as_draft: bool = True) -> Dict:
        """创建产品"""
        # 构建产品数据
        shopify_product = {
            "product": {
                "title": product_data.get("optimized_title") or product_data.get("original_title"),
                "body_html": product_data.get("optimized_description") or product_data.get("original_description"),
                "vendor": product_data.get("vendor", ""),
                "product_type": product_data.get("category", ""),
                "tags": product_data.get("tags", []),
                "status": "draft" if as_draft else "active",
                "metafields": [],
            }
        }
        
        # SEO 信息
        if product_data.get("meta_title"):
            shopify_product["product"]["metafields_global_title_tag"] = product_data["meta_title"]
        if product_data.get("meta_description"):
            shopify_product["product"]["metafields_global_description_tag"] = product_data["meta_description"]
        
        # URL Handle
        if product_data.get("url_handle"):
            shopify_product["product"]["handle"] = product_data["url_handle"]
        
        # 变体
        variants = product_data.get("variants", [])
        if variants:
            shopify_product["product"]["variants"] = [
                {
                    "sku": v.get("sku"),
                    "price": str(v.get("price", 0)),
                    "inventory_quantity": v.get("quantity", 0),
                    "option1": v.get("option1"),
                    "option2": v.get("option2"),
                    "weight": v.get("weight"),
                    "weight_unit": v.get("weight_unit", "kg"),
                }
                for v in variants
            ]
        else:
            # 单一变体
            shopify_product["product"]["variants"] = [{
                "sku": product_data.get("sku"),
                "price": str(product_data.get("original_price", 0)),
                "inventory_quantity": product_data.get("quantity", 0),
            }]
        
        # 图片
        images = product_data.get("images", [])
        if images:
            if isinstance(images, str):
                images = json.loads(images)
            shopify_product["product"]["images"] = [
                {"src": img} for img in images[:10]
            ]
        
        result = await self._request("POST", "products.json", data=shopify_product)
        return result.get("product")
    
    async def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """更新产品"""
        shopify_product = {"product": {"id": int(product_id)}}
        
        if product_data.get("optimized_title"):
            shopify_product["product"]["title"] = product_data["optimized_title"]
        if product_data.get("optimized_description"):
            shopify_product["product"]["body_html"] = product_data["optimized_description"]
        
        result = await self._request("PUT", f"products/{product_id}.json", data=shopify_product)
        return result.get("product")
    
    async def delete_product(self, product_id: str) -> bool:
        """删除产品"""
        try:
            await self._request("DELETE", f"products/{product_id}.json")
            return True
        except:
            return False
    
    async def publish_product(self, product_id: str) -> Dict:
        """发布产品（从草稿变为活跃）"""
        return await self.update_product(product_id, {"status": "active"})
    
    async def unpublish_product(self, product_id: str) -> Dict:
        """取消发布产品"""
        return await self.update_product(product_id, {"status": "draft"})
    
    async def upload_image(self, product_id: str, image_url: str, position: int = 1) -> Dict:
        """上传图片到产品"""
        data = {
            "image": {
                "src": image_url,
                "position": position,
            }
        }
        result = await self._request("POST", f"products/{product_id}/images.json", data=data)
        return result.get("image")
    
    async def get_inventory_levels(self, location_id: Optional[str] = None) -> List[Dict]:
        """获取库存水平"""
        params = {}
        if location_id:
            params["location_ids"] = location_id
        
        result = await self._request("GET", "inventory_levels.json", params=params)
        return result.get("inventory_levels", [])
    
    async def update_inventory(self, inventory_item_id: str, location_id: str, quantity: int) -> Dict:
        """更新库存"""
        data = {
            "location_id": int(location_id),
            "inventory_item_id": int(inventory_item_id),
            "available": quantity,
        }
        result = await self._request("POST", "inventory_levels/set.json", data=data)
        return result.get("inventory_level")


class ShopifyClientCache:
    """Shopify 客户端缓存"""
    
    _cache: Dict[int, tuple] = {}  # store_id -> (client, expiry)
    _ttl = timedelta(hours=1)
    
    @classmethod
    def get_client(cls, store: Store) -> ShopifyClient:
        """获取或创建客户端"""
        now = datetime.utcnow()
        
        if store.id in cls._cache:
            client, expiry = cls._cache[store.id]
            if now < expiry:
                return client
        
        client = ShopifyClient(store)
        cls._cache[store.id] = (client, now + cls._ttl)
        return client
    
    @classmethod
    def invalidate(cls, store_id: int):
        """使缓存失效"""
        cls._cache.pop(store_id, None)
