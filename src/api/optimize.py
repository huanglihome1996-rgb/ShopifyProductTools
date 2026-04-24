"""
AI 优化 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import Product
from src.schemas import ProductOptimize, ProductResponse, MessageResponse
from src.services.ai_optimizer import optimize_product

router = APIRouter()


@router.post("/{product_id}", response_model=MessageResponse)
async def optimize_single_product(
    product_id: int,
    options: ProductOptimize = ProductOptimize(),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """优化单个产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 执行优化
    optimized_data = await optimize_product(
        product=product,
        optimize_title=options.optimize_title,
        optimize_description=options.optimize_description,
        optimize_seo=options.optimize_seo,
        process_images=options.process_images,
    )
    
    # 更新产品
    if optimized_data.get("title"):
        product.optimized_title = optimized_data["title"]
    if optimized_data.get("description"):
        product.optimized_description = optimized_data["description"]
    if optimized_data.get("meta_title"):
        product.meta_title = optimized_data["meta_title"]
    if optimized_data.get("meta_description"):
        product.meta_description = optimized_data["meta_description"]
    if optimized_data.get("url_handle"):
        product.url_handle = optimized_data["url_handle"]
    
    product.status = "optimized"
    await db.commit()
    
    return MessageResponse(
        success=True,
        message="产品优化完成",
        data=optimized_data
    )


@router.post("/batch", response_model=MessageResponse)
async def optimize_batch_products(
    product_ids: List[int],
    options: ProductOptimize = ProductOptimize(),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """批量优化产品"""
    if len(product_ids) > 100:
        raise HTTPException(status_code=400, detail="单次最多优化 100 个产品")
    
    result = await db.execute(
        select(Product).where(Product.id.in_(product_ids))
    )
    products = result.scalars().all()
    
    if not products:
        raise HTTPException(status_code=404, detail="未找到产品")
    
    success_count = 0
    for product in products:
        try:
            optimized_data = await optimize_product(
                product=product,
                optimize_title=options.optimize_title,
                optimize_description=options.optimize_description,
                optimize_seo=options.optimize_seo,
                process_images=options.process_images,
            )
            
            if optimized_data.get("title"):
                product.optimized_title = optimized_data["title"]
            if optimized_data.get("description"):
                product.optimized_description = optimized_data["description"]
            if optimized_data.get("meta_title"):
                product.meta_title = optimized_data["meta_title"]
            if optimized_data.get("meta_description"):
                product.meta_description = optimized_data["meta_description"]
            if optimized_data.get("url_handle"):
                product.url_handle = optimized_data["url_handle"]
            
            product.status = "optimized"
            success_count += 1
        except Exception as e:
            print(f"优化产品 {product.id} 失败: {e}")
    
    await db.commit()
    
    return MessageResponse(
        success=True,
        message=f"批量优化完成，成功 {success_count}/{len(products)} 个",
        data={"success_count": success_count, "total": len(products)}
    )


@router.get("/preview/{product_id}", response_model=ProductResponse)
async def preview_optimization(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """预览优化结果（不保存）"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 执行优化但不保存
    optimized_data = await optimize_product(product)
    
    # 返回预览数据
    preview = ProductResponse.model_validate(product)
    if optimized_data.get("title"):
        preview.optimized_title = optimized_data["title"]
    if optimized_data.get("description"):
        preview.optimized_description = optimized_data["description"]
    
    return preview
