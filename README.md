# ShopifyProductTools

Shopify 产品批量管理工具 - 支持多店铺、AI 优化、多数据源导入。

## 功能特性

### 核心功能
- **多店铺管理** - 支持管理多个 Shopify 店铺，Token 加密存储
- **产品管理** - 产品 CRUD、SKU 去重、状态追踪
- **批量导入** - Excel/CSV 导入，Amazon/AliExpress/1688/独立站链接爬取
- **AI 优化** - 标题/描述/SEO 自动优化，图片处理
- **导入历史** - 批次追踪，成功/跳过/失败统计

### 技术栈
- **后端**: Python 3.13 + FastAPI + SQLAlchemy (异步)
- **数据库**: SQLite (可切换 PostgreSQL/MySQL)
- **前端**: Vue 3 + TypeScript + Vite + Element Plus
- **AI**: 支持 OpenAI/自定义 API

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+

### 后端安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入配置
```

### 前端安装

```bash
cd frontend
npm install
```

### 启动服务

```bash
# 后端 (端口 8000)
source venv/bin/activate
uvicorn src.app:app --reload --port 8000

# 前端 (端口 3000)
cd frontend
npm run dev
```

访问 http://localhost:3000 使用 Web 界面。

## 配置说明

### 环境变量 (.env)

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/shopify_tools.db

# 安全
SECRET_KEY=your-secret-key-here
TOKEN_ENCRYPTION_KEY=your-32-char-encryption-key

# AI 服务 (可选)
AI_API_KEY=your-openai-api-key
AI_BASE_URL=https://api.openai.com/v1
```

### Shopify Access Token

1. 在 Shopify 后台创建私有 App
2. 获取 Admin API Access Token
3. 在店铺管理页面添加店铺和 Token

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stores/` | GET/POST | 店铺列表/创建 |
| `/api/products/` | GET/POST | 产品列表/创建 |
| `/api/imports/excel` | POST | Excel 导入 |
| `/api/imports/url` | POST | URL 批量导入 |
| `/api/optimize/{id}` | POST | AI 优化产品 |

## 开发指南

### 项目结构

```
ShopifyProductTools/
├── src/
│   ├── api/           # API 路由
│   ├── models/        # 数据模型
│   ├── services/      # 业务逻辑
│   ├── utils/         # 工具函数
│   ├── app.py         # FastAPI 应用
│   └── config.py      # 配置管理
├── frontend/
│   └── src/
│       ├── views/     # 页面组件
│       ├── api/       # API 封装
│       └── router/    # 路由配置
├── tests/             # 测试文件
└── data/              # 数据目录
```

### 运行测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

### 代码规范

```bash
# 格式化
black src/ tests/

# 类型检查
mypy src/

# Lint
ruff check src/
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t shopify-tools .

# 运行容器
docker run -d -p 8000:8000 -v ./data:/app/data shopify-tools
```

### 生产环境

1. 使用 PostgreSQL/MySQL 替换 SQLite
2. 配置 HTTPS
3. 设置环境变量 `DEBUG=false`
4. 使用 Gunicorn + Uvicorn workers

## License

MIT
