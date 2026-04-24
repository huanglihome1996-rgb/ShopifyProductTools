"""
网站爬取服务 - 支持 Amazon, AliExpress, 1688, 独立站
"""
import asyncio
import json
import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import async_session
from src.models import Product, Variant, ImportHistory, OperationLog


# 平台特定选择器配置
PLATFORM_SELECTORS = {
    "amazon": {
        "title": ["#productTitle", "h1.a-size-large"],
        "price": [".a-price .a-offscreen", "#priceblock_ourprice", "#priceblock_dealprice"],
        "description": ["#productDescription", "#feature-bullets"],
        "images": ["#altImages img", "#imageBlock img", "#landingImage"],
        "specs": ["#productDetails_techSpec_section_1 tr"],
    },
    "aliexpress": {
        "title": ["h1.product-title-text", ".product-title"],
        "price": [".product-price-value", ".uniform-banner-box-price"],
        "description": [".product-description"],
        "images": [".images-view-item img", ".product-preview img"],
        "specs": [".product-params tr"],
    },
    "1688": {
        "title": [".d-title", "h1.title"],
        "price": [".price-value", ".original-price"],
        "description": [".desc-content", "#mod-detail-description"],
        "images": [".tab-content img", ".detail-gallery-img"],
        "specs": [".offer-attr-list li"],
    },
    "website": {
        # 通用选择器，需要智能识别
        "title": ["h1", "h1.product-title", "h1.product-name", "[itemprop='name']"],
        "price": [".price", "[itemprop='price']", ".product-price", ".current-price"],
        "description": ["[itemprop='description']", ".product-description", "#description"],
        "images": ["img[itemprop='image']", ".product-image img", ".gallery img"],
    },
}


async def scrape_products(
    urls: List[str],
    platform: str,
    store_id: int,
    batch_id: str,
):
    """爬取产品数据"""
    async with async_session() as db:
        try:
            # 更新导入记录
            result = await db.execute(
                select(ImportHistory).where(ImportHistory.batch_id == batch_id)
            )
            import_record = result.scalar_one_or_none()
            if import_record:
                import_record.status = "processing"
                await db.commit()

            success_count = 0
            fail_count = 0

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                
                for url in urls:
                    try:
                        page = await context.new_page()
                        product_data = await scrape_single_page(page, url, platform)
                        await page.close()

                        if product_data:
                            # 创建产品
                            product = Product(
                                store_id=store_id,
                                sku=product_data.get("sku") or f"scrape_{uuid.uuid4().hex[:8]}",
                                original_title=product_data.get("title", ""),
                                original_description=product_data.get("description"),
                                original_price=product_data.get("price"),
                                original_images=json.dumps(product_data.get("images", [])),
                                source_type=platform,
                                source_url=url,
                                tags=json.dumps(product_data.get("tags", [])),
                                status="pending",
                                is_draft=True,
                            )
                            db.add(product)
                            success_count += 1
                        else:
                            fail_count += 1

                    except Exception as e:
                        fail_count += 1
                        log = OperationLog(
                            operation_type="scrape",
                            target_type="product",
                            action="fail",
                            message=f"爬取 {url} 失败: {str(e)}",
                            is_success=False,
                        )
                        db.add(log)

                await browser.close()

            # 更新导入记录
            if import_record:
                import_record.success_count = success_count
                import_record.fail_count = fail_count
                import_record.status = "completed"
                import_record.finished_at = datetime.utcnow()
            
            await db.commit()

        except Exception as e:
            # 记录失败
            result = await db.execute(
                select(ImportHistory).where(ImportHistory.batch_id == batch_id)
            )
            import_record = result.scalar_one_or_none()
            if import_record:
                import_record.status = "failed"
                import_record.error_log = str(e)
                import_record.finished_at = datetime.utcnow()
            await db.commit()


async def scrape_single_page(page: Page, url: str, platform: str) -> Optional[Dict]:
    """爬取单个页面"""
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1000)  # 等待动态内容加载

        selectors = PLATFORM_SELECTORS.get(platform, PLATFORM_SELECTORS["website"])
        
        product_data = {
            "url": url,
            "title": None,
            "price": None,
            "description": None,
            "images": [],
            "specs": {},
        }

        # 提取标题
        for selector in selectors.get("title", []):
            try:
                element = await page.query_selector(selector)
                if element:
                    product_data["title"] = await element.inner_text()
                    break
            except:
                continue

        # 提取价格
        for selector in selectors.get("price", []):
            try:
                element = await page.query_selector(selector)
                if element:
                    price_text = await element.inner_text()
                    # 提取数字
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        product_data["price"] = float(price_match.group())
                    break
            except:
                continue

        # 提取描述
        for selector in selectors.get("description", []):
            try:
                element = await page.query_selector(selector)
                if element:
                    product_data["description"] = await element.inner_text()
                    break
            except:
                continue

        # 提取图片
        for selector in selectors.get("images", []):
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    src = await elem.get_attribute("src") or await elem.get_attribute("data-src")
                    if src and not src.startswith("data:"):
                        # 转换为绝对URL
                        if src.startswith("//"):
                            src = "https:" + src
                        elif not src.startswith("http"):
                            src = urljoin(url, src)
                        # 过滤小图标
                        if not any(x in src for x in ["icon", "logo", "avatar", "sprite"]):
                            product_data["images"].append(src)
                if product_data["images"]:
                    break
            except:
                continue

        # 去重图片
        product_data["images"] = list(dict.fromkeys(product_data["images"]))[:10]

        # 提取SKU（如果有）
        try:
            sku_elem = await page.query_selector("[itemprop='sku'], .sku, .product-sku, #ASIN")
            if sku_elem:
                product_data["sku"] = await sku_elem.inner_text()
        except:
            pass

        return product_data if product_data["title"] else None

    except Exception as e:
        print(f"爬取页面失败 {url}: {e}")
        return None


async def detect_platform(url: str) -> str:
    """自动检测平台类型"""
    domain = urlparse(url).netloc.lower()
    
    if "amazon" in domain:
        return "amazon"
    elif "aliexpress" in domain:
        return "aliexpress"
    elif "1688" in domain or "alibaba" in domain:
        return "1688"
    else:
        return "website"
