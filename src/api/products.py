"""
产品管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models import Product, Variant
from src.schemas import ProductCreate, ProductResponse, PaginatedResponse, MessageResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_products(
    store_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取产品列表（分页）"""
    query = select(Product)
    count_query = select(func.count(Product.id))
    
    if store_id:
        query = query.where(Product.store_id == store_id)
        count_query = count_query.where(Product.store_id == store_id)
    
    if status:
        query = query.where(Product.status == status)
        count_query = count_query.where(Product.status == status)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(Product.original_title.ilike(search_pattern))
        count_query = count_query.where(Product.original_title.ilike(search_pattern))
    
    # 获取总数
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Product.created_at.desc())
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ProductResponse.model_validate(p) for p in products]
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个产品详情"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建产品"""
    import json
    
    product = Product(
        store_id=product_data.store_id,
        sku=product_data.sku,
        original_title=product_data.original_title,
        original_description=product_data.original_description,
        original_price=product_data.original_price,
        original_images=json.dumps(product_data.original_images) if product_data.original_images else None,
        source_type=product_data.source_type,
        source_url=product_data.source_url,
        tags=json.dumps(product_data.tags) if product_data.tags else None,
        category=product_data.category,
    )
    
    db.add(product)
    await db.flush()  # 获取 product.id
    
    # 创建变体
    if product_data.variants:
        for variant_data in product_data.variants:
            variant = Variant(
                product_id=product.id,
                **variant_data.model_dump()
            )
            db.add(variant)
    
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    await db.delete(product)
    await db.commit()
    return MessageResponse(success=True, message="产品已删除")


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """通过 SKU 查询产品"""
    result = await db.execute(
        select(Product).where(Product.sku == sku, Product.store_id == store_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product
