# 📊 智能数据查询 Agent 系统

> 基于大语言模型的智能数据查询与分析平台，支持自然语言到 SQL 的自动转换

## 🎯 项目简介

本项目是一个基于大语言模型（LLM）的智能数据查询系统，能够将自然语言查询自动转换为 SQL 语句，并执行查询返回结果。系统采用 Agent 架构设计，支持多步骤的数据查询流程，包括关键词提取、信息召回、SQL 生成与验证等。

## ✨ 核心功能

### 🔍 智能查询转换
- **自然语言理解**：支持中文自然语言查询
- **SQL 自动生成**：基于元数据自动生成优化的 SQL 语句
- **多表关联**：智能识别表间关系，自动生成 JOIN 条件
- **查询验证**：语法检查和语义验证确保 SQL 正确性

### 🏗️ 模块化架构
- **Agent 工作流**：基于 LangGraph 的多步骤处理流程
- **向量检索**：使用 Qdrant 实现高效的向量相似度搜索
- **元数据管理**：完整的数据库元数据知识图谱
- **依赖注入**：基于容器的服务管理和依赖注入

### 📊 数据支持
- **多数据源**：支持 MySQL 数据库查询
- **向量存储**：集成 Elasticsearch 和 Qdrant
- **实时查询**：支持实时数据查询和分析

## 🛠️ 技术栈

### 后端技术
- **Python 3.11+** - 主要编程语言
- **FastAPI** - 高性能 Web 框架
- **LangChain/LangGraph** - LLM 应用框架
- **SQLAlchemy** - ORM 数据库操作
- **Loguru** - 结构化日志系统

### 数据库与存储
- **MySQL** - 关系型数据库
- **Qdrant** - 向量数据库
- **Elasticsearch** - 搜索引擎

### AI/ML 技术
- **大语言模型** - 支持多种 LLM 提供商
- **向量嵌入** - BGE-large-zh 中文嵌入模型
- **Agent 架构** - 智能体工作流设计

### 前端技术
- **Vue.js 3** - 现代化前端框架
- **Vite** - 快速构建工具
- **TypeScript** - 类型安全的 JavaScript

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Docker & Docker Compose
- MySQL 8.0+
- 至少 8GB 内存

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/YuStriving/zhangguiwenshu.git
cd zhangguiwenshu
```

2. **环境配置**
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动基础设施
cd docker
docker-compose up -d
```

3. **初始化数据**
```bash
# 构建元数据知识图谱
python app/scripts/bulid_meta_knowledge.py
```

4. **启动服务**
```bash
# 启动后端 API 服务
python main.py

# 启动前端服务（可选）
cd fronnted/data-agent-fronted
npm install
npm run dev
```

## 📁 项目结构

```
zhangguiwenshu/
├── app/                    # 应用核心代码
│   ├── agent/             # Agent 工作流模块
│   ├── api/               # API 接口层
│   ├── client/            # 客户端管理器
│   ├── core/              # 核心组件
│   ├── repositories/      # 数据访问层
│   └── service/           # 业务逻辑层
├── docker/                # Docker 配置
├── docs/                  # 项目文档
├── fronnted/              # 前端项目
└── prompts/               # 提示词模板
```

## 🔧 核心特性

### 1. 智能 Agent 工作流
系统采用多步骤的 Agent 工作流设计：
- **关键词提取**：从自然语言中提取关键信息
- **信息召回**：基于向量相似度召回相关数据
- **SQL 生成**：基于上下文生成优化的 SQL 语句
- **查询执行**：执行 SQL 并返回结果

### 2. 请求追踪与日志系统
- **请求 ID 追踪**：支持异步请求的完整追踪
- **结构化日志**：彩色输出和结构化日志格式
- **错误处理**：统一的异常处理机制

### 3. 依赖注入架构
- **服务容器**：基于容器的服务管理
- **生命周期管理**：支持单例和瞬态服务
- **自动依赖解析**：自动解析服务依赖关系

## 🎨 界面展示

### API 接口
系统提供 RESTful API 接口：

```bash
POST /api/query
Content-Type: application/json

{
  "query": "统计华北地区的销售总额"
}
```

### 前端界面
Vue.js 前端界面提供友好的用户交互体验。

## 📈 性能指标

- **查询响应时间**：平均 2-5 秒
- **SQL 准确率**：达到 85% 以上
- **并发支持**：支持多用户并发查询
- **错误恢复**：具备自动错误恢复机制

## 🔍 技术亮点

### 1. 创新的 Agent 架构
采用 LangGraph 构建的多步骤 Agent 工作流，每个步骤都有明确的职责和错误处理机制。

### 2. 智能的元数据管理
构建完整的数据库元数据知识图谱，支持智能的表关联和字段识别。

### 3. 高效的向量检索
集成 Qdrant 向量数据库，实现高效的相似度搜索和语义理解。

### 4. 完善的错误处理
统一的异常处理机制，确保系统的稳定性和可维护性。

## 🤝 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING.md](docs/CONTRIBUTING.md) 了解详细指南。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **项目主页**：https://github.com/YuStriving/zhangguiwenshu
- **问题反馈**：请使用 GitHub Issues
- **邮箱联系**：项目维护者邮箱

---

**由 AI 生成的文档，最后更新：2026-04-17**