# IMPLEMENTATION_PLAN.md

# ShopifyProductTools 实施计划

> 生成时间: 2024-04-23
> 状态: Phase 2 规划完成，待实施

---

## 项目概述

构建一个 Shopify 产品管理工具，支持批量导入、AI 优化、多店铺管理和 Web 界面。

**技术栈:** Python + FastAPI + SQLite + Web UI (Vue.js/React)

---

## 优先级排序

### P0 - 核心基础 (必须首先完成)

- [ ] **项目结构搭建**
  - 创建 FastAPI 项目结构
  - 配置依赖管理 (requirements.txt)
  - 设置开发环境 (venv, pytest, ruff)
  - 创建配置管理模块

- [ ] **数据模型设计**
  - Product 模型 (产品基础信息)
  - Variant 模型 (产品变体)
  - Store 模型 (店铺配置)
  - ImportHistory 模型 (导入历史)
  - 使用 Pydantic + SQLAlchemy

- [ ] **SQLite 数据库初始化**
  - 数据库连接管理
  - 表结构创建
  - CRUD 基础操作

### P1 - Shopify 集成

- [ ] **Shopify API 客户端**
  - API 连接封装
  - Token 管理和加密存储
  - 多店铺支持
  - 错误处理和重试机制

- [ ] **产品上传功能**
  - 产品创建 API 调用
  - 变体上传
  - 多图上传
  - 草稿状态设置

- [ ] **产品匹配逻辑**
  - SKU 查询
  - 已存在产品跳过
  - 操作日志记录

### P2 - 数据导入

- [ ] **Excel 导入模块**
  - 文件解析 (openpyxl)
  - 列映射配置
  - 数据验证
  - 批量处理 (100个/批)

- [ ] **网站爬取模块**
  - Amazon 产品抓取
  - AliExpress 产品抓取
  - 1688 产品抓取
  - 通用独立站抓取
  - 反爬处理 (Playwright/Selenium)

- [ ] **导入控制器**
  - 进度追踪
  - 失败重试
  - 错误报告生成

### P3 - AI 优化

- [ ] **标题优化服务**
  - AI API 集成 (OpenAI/Anthropic)
  - 关键词插入
  - 长度控制
  - 冗余词去除

- [ ] **描述生成服务**
  - 营销风格描述生成
  - 关键信息保留
  - 多段落结构

- [ ] **SEO 优化服务**
  - Meta title 生成
  - Meta description 生成
  - URL handle 生成

- [ ] **图片处理服务**
  - 尺寸统一
  - 压缩优化
  - 格式转换

### P4 - Web 界面

- [ ] **前端项目搭建**
  - Vue.js/React 项目初始化
  - UI 组件库选择 (Element Plus/Ant Design)
  - 路由配置

- [ ] **店铺管理页面**
  - 店铺列表
  - 添加/编辑/删除店铺
  - Token 输入和加密存储

- [ ] **产品导入页面**
  - Excel 上传组件
  - 列映射配置界面
  - 网站链接批量输入
  - 导入进度显示

- [ ] **产品优化页面**
  - 产品列表展示
  - 优化预览对比
  - 批量优化操作

- [ ] **产品上传页面**
  - 待上传列表
  - 上传进度
  - 二次确认上架

- [ ] **历史记录页面**
  - 导入历史
  - 操作日志
  - 错误报告

- [ ] **仪表盘**
  - 统计概览
  - 最近操作
  - 待处理任务

### P5 - 完善和测试

- [ ] **单元测试**
  - API 测试
  - 服务层测试
  - 数据模型测试

- [ ] **集成测试**
  - 导入流程测试
  - 优化流程测试
  - 上传流程测试

- [ ] **文档完善**
  - API 文档 (FastAPI Swagger)
  - 用户使用文档
  - 部署文档

---

## 技术决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 后端框架 | FastAPI | 高性能、异步支持、自动文档 |
| 数据库 | SQLite | 轻量级、本地存储、无需额外服务 |
| ORM | SQLAlchemy + Pydantic | 类型安全、验证支持 |
| 网页抓取 | Playwright | 反爬能力强、支持动态渲染 |
| Excel 处理 | openpyxl | 功能完整、性能好 |
| AI API | OpenAI/Anthropic | 成熟稳定、效果好 |
| 图片处理 | Pillow | Python 标准库 |
| 前端框架 | Vue.js 3 | 易上手、生态完善 |
| UI 组件 | Element Plus | 组件丰富、文档完善 |

---

## 依赖列表

### 后端核心
```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.5.0
python-multipart>=0.0.6
aiohttp>=3.9.0
```

### 数据处理
```
openpyxl>=3.1.0
pandas>=2.1.0
pillow>=10.0.0
```

### 网页抓取
```
playwright>=1.40.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
```

### AI 集成
```
openai>=1.10.0
anthropic>=0.18.0
```

### 开发工具
```
pytest>=7.4.0
pytest-asyncio>=0.23.0
ruff>=0.1.0
black>=24.0.0
mypy>=1.8.0
```

---

## 下一步

运行 `./loop.sh build` 开始 Phase 3 构建阶段，按优先级依次实现各模块。
