"""
Pydantic Schema 定义
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


# ============ Store Schemas ============

class StoreBase(BaseModel):
    name: str = Field(..., max_length=100)
    shop_url: str = Field(..., max_length=255)


class StoreCreate(StoreBase):
    access_token: str


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    access_token: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Variant Schemas ============

class VariantBase(BaseModel):
    sku: str
    title: str
    option1: Optional[str] = None
    option2: Optional[str] = None
    option3: Optional[str] = None
    price: float = 0.0
    quantity: int = 0
    weight: Optional[float] = None
    weight_unit: str = "kg"
    image_url: Optional[str] = None


class VariantCreate(VariantBase):
    pass


class VariantResponse(VariantBase):
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Product Schemas ============

class ProductBase(BaseModel):
    sku: str
    original_title: str
    original_description: Optional[str] = None
    original_price: Optional[float] = None
    original_images: Optional[List[str]] = None
    source_type: str
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class ProductCreate(ProductBase):
    store_id: int
    variants: Optional[List[VariantCreate]] = None


class ProductOptimize(BaseModel):
    """产品优化请求"""
    optimize_title: bool = True
    optimize_description: bool = True
    optimize_seo: bool = True
    process_images: bool = True


class ProductResponse(ProductBase):
    id: int
    store_id: int
    shopify_id: Optional[str] = None
    optimized_title: Optional[str] = None
    optimized_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    url_handle: Optional[str] = None
    status: str
    is_draft: bool
    created_at: datetime
    updated_at: datetime
    variants: List[VariantResponse] = []

    class Config:
        from_attributes = True


# ============ Import Schemas ============

class ColumnMapping(BaseModel):
    """Excel 列映射配置"""
    title: str = Field(..., description="标题列名")
    description: Optional[str] = Field(None, description="描述列名")
    price: Optional[str] = Field(None, description="价格列名")
    sku: Optional[str] = Field(None, description="SKU列名")
    quantity: Optional[str] = Field(None, description="库存列名")
    images: Optional[str] = Field(None, description="图片列名（多图用分隔符）")
    tags: Optional[str] = Field(None, description="标签列名")
    category: Optional[str] = Field(None, description="分类列名")
    variant_option1: Optional[str] = Field(None, description="变体选项1列名（如颜色）")
    variant_option2: Optional[str] = Field(None, description="变体选项2列名（如尺寸）")


class ImportExcelRequest(BaseModel):
    """Excel 导入请求"""
    store_id: int
    column_mapping: ColumnMapping
    image_separator: str = Field(default=",", description="图片URL分隔符")


class ImportUrlRequest(BaseModel):
    """网站链接导入请求"""
    store_id: int
    urls: List[str]
    platform: str = Field(default="website", description="平台类型: amazon, aliexpress, 1688, website")


class ImportHistoryResponse(BaseModel):
    """导入历史响应"""
    id: int
    batch_id: str
    source_type: str
    source_name: str
    total_count: int
    success_count: int
    skip_count: int
    fail_count: int
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Common Schemas ============

class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    items: List


class MessageResponse(BaseModel):
    """通用消息响应"""
    success: bool
    message: str
    data: Optional[dict] = None
