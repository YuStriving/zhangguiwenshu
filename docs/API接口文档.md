# API接口文档

## 1. 接口概述

### 1.1 接口设计原则
- RESTful API设计风格
- JSON格式数据交换
- 异步处理支持
- 统一的错误处理机制

### 1.2 认证与授权
- JWT Token认证（待实现）
- API Key认证（待实现）
- 基于角色的访问控制（待实现）

### 1.3 响应格式
```json
{
    "code": 200,
    "message": "成功",
    "data": {},
    "timestamp": "2026-04-13T10:30:00Z"
}
```

## 2. 元数据管理接口

### 2.1 表信息管理

#### 2.1.1 获取表列表
**接口**: `GET /api/v1/tables`

**请求参数**:
```json
{
    "page": 1,
    "size": 20,
    "role": "dim"
}
```

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "total": 100,
        "tables": [
            {
                "id": "user_table",
                "name": "用户表",
                "role": "dim",
                "description": "用户维度表",
                "column_count": 15,
                "created_at": "2026-04-13T10:00:00Z"
            }
        ]
    }
}
```

#### 2.1.2 获取表详情
**接口**: `GET /api/v1/tables/{table_id}`

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "id": "user_table",
        "name": "用户表",
        "role": "dim",
        "description": "用户维度表",
        "columns": [
            {
                "id": "user_table_user_id",
                "name": "user_id",
                "type": "varchar",
                "role": "primary_key",
                "description": "用户ID",
                "examples": ["001", "002", "003"],
                "alias": ["用户编号", "用户标识"]
            }
        ],
        "metrics": [
            {
                "id": "user_count",
                "name": "用户数量",
                "description": "用户数量统计"
            }
        ]
    }
}
```

#### 2.1.3 创建/更新表信息
**接口**: `POST /api/v1/tables`

**请求数据**:
```json
{
    "id": "user_table",
    "name": "用户表",
    "role": "dim",
    "description": "用户维度表"
}
```

### 2.2 列信息管理

#### 2.2.1 获取列列表
**接口**: `GET /api/v1/tables/{table_id}/columns`

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "table_id": "user_table",
        "columns": [
            {
                "id": "user_table_user_id",
                "name": "user_id",
                "type": "varchar",
                "role": "primary_key",
                "description": "用户ID",
                "examples": ["001", "002", "003"],
                "alias": ["用户编号", "用户标识"]
            }
        ]
    }
}
```

#### 2.2.2 获取列详情
**接口**: `GET /api/v1/columns/{column_id}`

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "id": "user_table_user_id",
        "name": "user_id",
        "type": "varchar",
        "role": "primary_key",
        "description": "用户ID",
        "examples": ["001", "002", "003"],
        "alias": ["用户编号", "用户标识"],
        "table_id": "user_table",
        "table_name": "用户表",
        "related_metrics": [
            {
                "id": "user_count",
                "name": "用户数量"
            }
        ]
    }
}
```

### 2.3 指标信息管理

#### 2.3.1 获取指标列表
**接口**: `GET /api/v1/metrics`

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "metrics": [
            {
                "id": "user_count",
                "name": "用户数量",
                "description": "用户数量统计",
                "relevant_columns": ["user_id"],
                "alias": ["用户总数", "用户数量"]
            }
        ]
    }
}
```

## 3. 搜索接口

### 3.1 向量搜索
**接口**: `POST /api/v1/search/vector`

**请求数据**:
```json
{
    "query": "用户年龄相关的列",
    "top_k": 10,
    "threshold": 0.7
}
```

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "query": "用户年龄相关的列",
        "results": [
            {
                "id": "user_table_age",
                "name": "age",
                "type": "int",
                "role": "dimension",
                "description": "用户年龄",
                "table_id": "user_table",
                "table_name": "用户表",
                "score": 0.95,
                "match_type": "vector"
            }
        ],
        "total": 5
    }
}
```

### 3.2 全文搜索
**接口**: `POST /api/v1/search/text`

**请求数据**:
```json
{
    "query": "用户表",
    "page": 1,
    "size": 20
}
```

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "query": "用户表",
        "results": [
            {
                "id": "user_table",
                "name": "用户表",
                "role": "dim",
                "description": "用户维度表",
                "match_type": "text",
                "highlight": "<em>用户</em>表"
            }
        ],
        "total": 3
    }
}
```

### 3.3 混合搜索
**接口**: `POST /api/v1/search/hybrid`

**请求数据**:
```json
{
    "query": "用户相关的表和列",
    "vector_weight": 0.6,
    "text_weight": 0.4,
    "top_k": 20
}
```

## 4. 数据同步接口

### 4.1 同步数据仓库表结构
**接口**: `POST /api/v1/sync/tables`

**请求数据**:
```json
{
    "table_names": ["user_table", "order_table"],
    "force_refresh": false
}
```

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "synced_tables": 2,
        "synced_columns": 25,
        "errors": [],
        "duration": "5.2s"
    }
}
```

### 4.2 构建向量索引
**接口**: `POST /api/v1/index/vector`

**请求数据**:
```json
{
    "table_ids": ["user_table", "order_table"],
    "rebuild": false
}
```

### 4.3 构建全文索引
**接口**: `POST /api/v1/index/text`

## 5. 系统管理接口

### 5.1 健康检查
**接口**: `GET /api/v1/health`

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "status": "healthy",
        "services": {
            "mysql_meta": "healthy",
            "mysql_dw": "healthy",
            "qdrant": "healthy",
            "elasticsearch": "healthy",
            "embedding": "healthy"
        },
        "timestamp": "2026-04-13T10:30:00Z"
    }
}
```

### 5.2 系统状态
**接口**: `GET /api/v1/status`

**响应数据**:
```json
{
    "code": 200,
    "data": {
        "version": "1.0.0",
        "uptime": "3天2小时",
        "statistics": {
            "tables": 50,
            "columns": 500,
            "metrics": 30,
            "vector_embeddings": 580,
            "search_documents": 580
        },
        "performance": {
            "avg_response_time": "120ms",
            "qps": 15.2
        }
    }
}
```

## 6. 错误码说明

### 6.1 通用错误码
| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 6.2 业务错误码
| 错误码 | 说明 |
|--------|------|
| 1001 | 表不存在 |
| 1002 | 列不存在 |
| 1003 | 指标不存在 |
| 2001 | 数据同步失败 |
| 2002 | 索引构建失败 |
| 3001 | 搜索服务不可用 |

## 7. 接口调用示例

### 7.1 Python调用示例
```python
import requests
import json

# 基础配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# 搜索示例
def search_metadata(query: str):
    url = f"{BASE_URL}/api/v1/search/hybrid"
    data = {
        "query": query,
        "top_k": 10
    }
    
    response = requests.post(url, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"搜索失败: {response.text}")

# 获取表详情示例
def get_table_details(table_id: str):
    url = f"{BASE_URL}/api/v1/tables/{table_id}"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"获取表详情失败: {response.text}")
```

### 7.2 curl调用示例
```bash
# 搜索接口
curl -X POST "http://localhost:8000/api/v1/search/vector" \
  -H "Content-Type: application/json" \
  -d '{"query": "用户年龄", "top_k": 5}'

# 获取表列表
curl -X GET "http://localhost:8000/api/v1/tables?page=1&size=10"

# 健康检查
curl -X GET "http://localhost:8000/api/v1/health"
```

---

**版本**: 1.0  
**作者**: AI生成  
**更新日期**: 2026-04-13