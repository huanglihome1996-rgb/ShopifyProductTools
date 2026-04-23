# ShopifyProductTools 需求概述

## JTBD（待完成任务）

**帮助 Shopify 商家高效管理产品**，通过自动化工具实现批量导入、智能优化和一键上传，减少重复劳动，提升运营效率。

## 主题列表

| 主题 | 规格文件 | 描述 |
|------|----------|------|
| 数据导入 | specs/data-import.md | 从 Excel 和网站链接导入产品信息 |
| 产品优化 | specs/product-optimization.md | AI 驱动的标题、描述、SEO 和图片优化 |
| Shopify 集成 | specs/shopify-integration.md | 多店铺管理、产品上传和数据导出 |
| Web 界面 | specs/web-interface.md | 用户操作界面 |

## 核心功能

1. **批量导入** - Excel 文件和网站链接（Amazon/AliExpress/1688/独立站）
2. **智能优化** - AI 生成标题、描述、SEO 信息，图片处理
3. **多店铺管理** - Token 缓存，店铺切换
4. **安全上传** - 草稿状态，用户二次确认
5. **历史记录** - 本地数据库缓存，操作日志

## 技术栈

- 后端：Python (FastAPI)
- 前端：Web 界面
- 数据库：SQLite
- AI：用于标题/描述/SEO 生成
- API：Shopify Admin API

## 数据量

- 单次导入上限：100 个商品
- 支持上千级产品管理

## 下一步

进入 Phase 2: 规划阶段，生成 IMPLEMENTATION_PLAN.md
