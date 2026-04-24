"""
店铺管理 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import Store
from src.schemas import StoreCreate, StoreUpdate, StoreResponse, MessageResponse
from src.utils.crypto import encrypt_token, decrypt_token

router = APIRouter()


@router.get("/", response_model=List[StoreResponse])
async def list_stores(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取店铺列表"""
    result = await db.execute(select(Store).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个店铺"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return store


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    store_data: StoreCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建店铺"""
    # 加密 token
    encrypted_token = encrypt_token(store_data.access_token)
    
    store = Store(
        name=store_data.name,
        shop_url=store_data.shop_url,
        access_token=encrypted_token,
    )
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新店铺"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    update_data = store_data.model_dump(exclude_unset=True)
    
    # 如果更新 token，需要加密
    if "access_token" in update_data:
        update_data["access_token"] = encrypt_token(update_data["access_token"])
    
    for key, value in update_data.items():
        setattr(store, key, value)
    
    await db.commit()
    await db.refresh(store)
    return store


@router.delete("/{store_id}", response_model=MessageResponse)
async def delete_store(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除店铺"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    await db.delete(store)
    await db.commit()
    return MessageResponse(success=True, message="店铺已删除")
