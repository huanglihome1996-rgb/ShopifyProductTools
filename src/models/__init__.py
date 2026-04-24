"""
数据模型定义
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Store(Base):
    """店铺模型"""
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    shop_url: Mapped[str] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(Text)  # 加密存储
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    products: Mapped[List["Product"]] = relationship(back_populates="store")


class Product(Base):
    """产品模型"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))
    sku: Mapped[str] = mapped_column(String(100), index=True)
    shopify_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 原始数据
    original_title: Mapped[str] = mapped_column(String(500))
    original_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    original_images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # 优化后数据
    optimized_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    optimized_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    url_handle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, optimized, uploaded, published
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 来源信息
    source_type: Mapped[str] = mapped_column(String(20))  # excel, amazon, aliexpress, 1688, website
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 分类标签
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    store: Mapped["Store"] = relationship(back_populates="products")
    variants: Mapped[List["Variant"]] = relationship(back_populates="product")


class Variant(Base):
    """产品变体模型"""
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    sku: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    option1: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 如颜色
    option2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 如尺寸
    option3: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    price: Mapped[float] = mapped_column(Float, default=0.0)
    compare_at_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str] = mapped_column(String(10), default="kg")
    
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    product: Mapped["Product"] = relationship(back_populates="variants")


class ImportHistory(Base):
    """导入历史记录"""
    __tablename__ = "import_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    batch_id: Mapped[str] = mapped_column(String(50), index=True)
    source_type: Mapped[str] = mapped_column(String(20))
    source_name: Mapped[str] = mapped_column(String(255))  # 文件名或URL
    
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    skip_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(20), default="processing")  # processing, completed, failed
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)


class OperationLog(Base):
    """操作日志"""
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    operation_type: Mapped[str] = mapped_column(String(50))  # import, optimize, upload, publish
    target_type: Mapped[str] = mapped_column(String(50))  # product, variant, batch
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    action: Mapped[str] = mapped_column(String(100))
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    
    is_success: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
