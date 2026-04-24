"""
Excel 导入服务
"""
import pandas as pd
import json
import uuid
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import async_session
from src.models import Product, Variant, ImportHistory, OperationLog


async def process_excel_import(
    content: bytes,
    filename: str,
    store_id: int,
    batch_id: str,
    column_mapping: Dict[str, str],
):
    """处理 Excel 导入"""
    async with async_session() as db:
        try:
            # 更新导入记录状态
            result = await db.execute(
                select(ImportHistory).where(ImportHistory.batch_id == batch_id)
            )
            import_record = result.scalar_one()
            import_record.status = "processing"
            await db.commit()
            
            # 解析 Excel
            if filename.endswith('.csv'):
                df = pd.read_csv(pd.io.common.BytesIO(content))
            else:
                df = pd.read_excel(pd.io.common.BytesIO(content))
            
            total_count = len(df)
            import_record.total_count = total_count
            
            # 限制最多 100 个
            if total_count > 100:
                df = df.head(100)
                import_record.total_count = 100
            
            success_count = 0
            skip_count = 0
            fail_count = 0
            
            # 处理每一行
            for idx, row in df.iterrows():
                try:
                    # 获取 SKU
                    sku_col = column_mapping.get("sku", "sku")
                    sku = str(row.get(sku_col, f"auto_{uuid.uuid4().hex[:8]}"))
                    
                    # 检查是否已存在（跳过）
                    existing = await db.execute(
                        select(Product).where(Product.sku == sku, Product.store_id == store_id)
                    )
                    if existing.scalar_one_or_none():
                        skip_count += 1
                        # 记录日志
                        log = OperationLog(
                            operation_type="import",
                            target_type="product",
                            action="skip",
                            message=f"SKU {sku} 已存在，跳过",
                            is_success=True,
                        )
                        db.add(log)
                        continue
                    
                    # 创建产品
                    title = str(row.get(column_mapping.get("title", "title"), ""))
                    if not title:
                        fail_count += 1
                        continue
                    
                    description = row.get(column_mapping.get("description", "description"))
                    price = row.get(column_mapping.get("price", "price"))
                    images = row.get(column_mapping.get("images", "images"))
                    tags = row.get(column_mapping.get("tags", "tags"))
                    category = row.get(column_mapping.get("category", "category"))
                    
                    product = Product(
                        store_id=store_id,
                        sku=sku,
                        original_title=title,
                        original_description=str(description) if description else None,
                        original_price=float(price) if price else None,
                        original_images=json.dumps(str(images).split(",")) if images else None,
                        source_type="excel",
                        source_url=filename,
                        tags=json.dumps(str(tags).split(",")) if tags else None,
                        category=str(category) if category else None,
                        status="pending",
                        is_draft=True,
                    )
                    db.add(product)
                    await db.flush()
                    
                    # 创建变体（如果有变体列）
                    option1_col = column_mapping.get("variant_option1")
                    option2_col = column_mapping.get("variant_option2")
                    
                    if option1_col or option2_col:
                        variant = Variant(
                            product_id=product.id,
                            sku=sku,
                            title=title,
                            option1=str(row.get(option1_col)) if option1_col else None,
                            option2=str(row.get(option2_col)) if option2_col else None,
                            price=float(price) if price else 0.0,
                            quantity=int(row.get(column_mapping.get("quantity", "quantity"), 0)),
                        )
                        db.add(variant)
                    
                    success_count += 1
                    
                except Exception as e:
                    fail_count += 1
                    log = OperationLog(
                        operation_type="import",
                        target_type="product",
                        action="fail",
                        message=f"行 {idx} 导入失败: {str(e)}",
                        is_success=False,
                    )
                    db.add(log)
            
            # 更新导入记录
            import_record.success_count = success_count
            import_record.skip_count = skip_count
            import_record.fail_count = fail_count
            import_record.status = "completed"
            import_record.finished_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            # 导入失败
            result = await db.execute(
                select(ImportHistory).where(ImportHistory.batch_id == batch_id)
            )
            import_record = result.scalar_one()
            import_record.status = "failed"
            import_record.error_log = str(e)
            import_record.finished_at = datetime.utcnow()
            await db.commit()


def generate_column_mapping_template() -> Dict[str, str]:
    """生成列映射模板"""
    return {
        "title": "title",
        "description": "description",
        "price": "price",
        "sku": "sku",
        "quantity": "quantity",
        "images": "images",
        "tags": "tags",
        "category": "category",
        "variant_option1": "color",
        "variant_option2": "size",
    }