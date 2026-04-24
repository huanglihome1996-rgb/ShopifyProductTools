"""
AI 优化服务 - 标题、描述、SEO 优化
"""
import json
import re
from typing import Dict, Optional, List
from openai import AsyncOpenAI
from PIL import Image
import httpx
import io

from src.config import settings
from src.models import Product


# AI 优化提示词模板
TITLE_PROMPT = """You are an expert e-commerce copywriter. Optimize the following product title for better conversion and SEO.

Original title: {title}

Requirements:
1. Keep it under 150 characters
2. Include key product features and benefits
3. Use power words that drive action
4. Maintain accuracy - don't make false claims
5. Format: [Brand/Product Name] + [Key Feature] + [Benefit] + [Spec if relevant]

Return ONLY the optimized title, nothing else."""

DESCRIPTION_PROMPT = """You are an expert e-commerce copywriter. Create a compelling product description based on the following information.

Title: {title}
Original description: {description}

Requirements:
1. Start with a hook that grabs attention
2. Use bullet points for key features (3-5 points)
3. Include benefits, not just features
4. Address customer pain points
5. End with a clear call-to-action
6. Keep it between 150-300 words
7. Use HTML formatting: <p> for paragraphs, <ul><li> for bullet points

Return the HTML formatted description."""

SEO_PROMPT = """You are an SEO expert. Generate SEO metadata for this product.

Title: {title}
Description: {description}

Return a JSON object with:
1. "meta_title": SEO title (max 60 characters, include main keyword)
2. "meta_description": Meta description (max 160 characters, compelling and relevant)
3. "url_handle": URL-friendly slug (lowercase, hyphens, no special chars)
4. "keywords": Array of 5-8 relevant keywords

Return ONLY valid JSON, no other text."""


async def optimize_product(
    product: Product,
    optimize_title: bool = True,
    optimize_description: bool = True,
    optimize_seo: bool = True,
    process_images: bool = True,
) -> Dict:
    """优化产品信息"""
    result = {}
    
    if not settings.ai_api_key:
        raise ValueError("AI API key not configured")

    client = AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url if settings.ai_base_url else None,
    )

    # 优化标题
    if optimize_title and product.original_title:
        try:
            response = await client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are an expert e-commerce copywriter."},
                    {"role": "user", "content": TITLE_PROMPT.format(title=product.original_title)}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            result["title"] = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"标题优化失败: {e}")
            result["title"] = product.original_title

    # 优化描述
    if optimize_description:
        try:
            desc = product.original_description or ""
            title = result.get("title") or product.original_title
            
            response = await client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are an expert e-commerce copywriter."},
                    {"role": "user", "content": DESCRIPTION_PROMPT.format(title=title, description=desc)}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            result["description"] = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"描述优化失败: {e}")

    # SEO 优化
    if optimize_seo:
        try:
            title = result.get("title") or product.original_title
            desc = result.get("description") or product.original_description or ""
            
            response = await client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Return only valid JSON."},
                    {"role": "user", "content": SEO_PROMPT.format(title=title, description=desc)}
                ],
                temperature=0.5,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            
            seo_data = json.loads(response.choices[0].message.content)
            result["meta_title"] = seo_data.get("meta_title", "")[:60]
            result["meta_description"] = seo_data.get("meta_description", "")[:160]
            result["url_handle"] = seo_data.get("url_handle", "")
            result["keywords"] = seo_data.get("keywords", [])
        except Exception as e:
            print(f"SEO优化失败: {e}")

    # 图片处理
    if process_images and product.original_images:
        try:
            images = json.loads(product.original_images) if isinstance(product.original_images, str) else product.original_images
            processed_images = await process_product_images(images)
            result["processed_images"] = processed_images
        except Exception as e:
            print(f"图片处理失败: {e}")

    return result


async def process_product_images(image_urls: List[str]) -> List[Dict]:
    """处理产品图片 - 压缩、调整尺寸"""
    processed = []
    
    async with httpx.AsyncClient(timeout=30) as client:
        for url in image_urls[:10]:  # 最多处理10张
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    continue
                
                # 打开图片
                img = Image.open(io.BytesIO(response.content))
                
                # 转换为 RGB（处理 PNG 透明背景）
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # 调整尺寸
                max_size = (settings.image_max_width, settings.image_max_height)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 压缩
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=settings.image_quality, optimize=True)
                
                processed.append({
                    "original_url": url,
                    "width": img.width,
                    "height": img.height,
                    "size": len(output.getvalue()),
                })
                
            except Exception as e:
                print(f"图片处理失败 {url}: {e}")
                continue
    
    return processed


async def generate_product_tags(product: Product) -> List[str]:
    """生成产品标签"""
    if not settings.ai_api_key:
        return []
    
    client = AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url if settings.ai_base_url else None,
    )
    
    try:
        response = await client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": "You are a product tagging expert."},
                {"role": "user", "content": f"""Generate 5-10 relevant product tags for:
Title: {product.original_title}
Description: {product.original_description or ''}

Return only a JSON array of lowercase tags, e.g., ["tag1", "tag2"]"""}
            ],
            temperature=0.5,
            max_tokens=100,
            response_format={"type": "json_object"},
        )
        
        tags = json.loads(response.choices[0].message.content)
        return tags if isinstance(tags, list) else tags.get("tags", [])
    except:
        return []
