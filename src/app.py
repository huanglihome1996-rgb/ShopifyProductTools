"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database import init_db, close_db
from src.api import stores, products, imports, optimize


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Shopify 产品管理工具 - 批量导入、AI优化、多店铺管理",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stores.router, prefix="/api/stores", tags=["店铺管理"])
app.include_router(products.router, prefix="/api/products", tags=["产品管理"])
app.include_router(imports.router, prefix="/api/imports", tags=["数据导入"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["AI优化"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}