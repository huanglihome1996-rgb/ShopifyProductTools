"""
数据导入 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models import ImportHistory, Product
from src.schemas import ImportExcelRequest, ImportUrlRequest, ImportHistoryResponse, MessageResponse
from src.schemas import PaginatedResponse
from src.services.excel_import import process_excel_import
from src.services.web_scraper import scrape_products

router = APIRouter()


@router.post("/excel", response_model=MessageResponse)
async def import_from_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    store_id: int = ...,
    title_column: str = "title",
    description_column: str = "description",
    price_column: str = "price",
    sku_column: str = "sku",
    db: AsyncSession = Depends(get_db)
):
    """从 Excel 文件导入产品"""
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="仅支持 Excel 文件 (.xlsx, .xls, .csv)")
    
    # 读取文件内容
    content = await file.read()
    
    # 创建导入记录
    import_record = ImportHistory(
        batch_id=f"batch_{store_id}_{file.filename}",
        source_type="excel",
        source_name=file.filename,
        store_id=store_id,
    )
    db.add(import_record)
    await db.commit()
    await db.refresh(import_record)
    
    # 后台处理导入
    background_tasks.add_task(
        process_excel_import,
        content=content,
        filename=file.filename,
        store_id=store_id,
        batch_id=import_record.batch_id,
        column_mapping={
            "title": title_column,
            "description": description_column,
            "price": price_column,
            "sku": sku_column,
        }
    )
    
    return MessageResponse(
        success=True,
        message=f"导入任务已创建，批次ID: {import_record.batch_id}",
        data={"batch_id": import_record.batch_id}
    )


@router.post("/urls", response_model=MessageResponse)
async def import_from_urls(
    request: ImportUrlRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """从网站链接导入产品"""
    if len(request.urls) > 100:
        raise HTTPException(status_code=400, detail="单次最多导入 100 个链接")
    
    # 创建导入记录
    import_record = ImportHistory(
        batch_id=f"batch_{request.store_id}_{request.platform}",
        source_type=request.platform,
        source_name=f"{len(request.urls)} URLs from {request.platform}",
        store_id=request.store_id,
        total_count=len(request.urls),
    )
    db.add(import_record)
    await db.commit()
    await db.refresh(import_record)
    
    # 后台处理爬取
    background_tasks.add_task(
        scrape_products,
        urls=request.urls,
        platform=request.platform,
        store_id=request.store_id,
        batch_id=import_record.batch_id,
    )
    
    return MessageResponse(
        success=True,
        message=f"爬取任务已创建，共 {len(request.urls)} 个链接",
        data={"batch_id": import_record.batch_id}
    )


@router.get("/history", response_model=PaginatedResponse)
async def get_import_history(
    store_id: int = None,
    page: int = 1,
    page_size: int = 20,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取导入历史"""
    # 获取总数
    count_query = select(func.count(ImportHistory.id))
    if store_id:
        count_query = count_query.where(ImportHistory.store_id == store_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = select(ImportHistory).order_by(ImportHistory.started_at.desc())
    
    if store_id:
        query = query.where(ImportHistory.store_id == store_id)
    
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ImportHistoryResponse.model_validate(item) for item in items]
    )


@router.get("/history/{batch_id}", response_model=ImportHistoryResponse)
async def get_import_detail(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单次导入详情"""
    result = await db.execute(
        select(ImportHistory).where(ImportHistory.batch_id == batch_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="导入记录不存在")
    return record
