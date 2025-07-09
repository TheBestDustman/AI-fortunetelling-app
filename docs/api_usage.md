# FastAPI 接口使用指南

本文档详细说明如何使用 AI 算命应用的 FastAPI 接口。

## 接口概述

AI 算命应用提供了以下 RESTful API 接口：

| 路径 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 欢迎页面，检查服务是否正常运行 |
| `/fortune` | POST | 获取初始算命结果 |
| `/chat` | POST | 与算命先生进行对话 |

## 启动服务

```bash
# 在项目根目录下运行
python app.py
```

服务将在 `http://127.0.0.1:8000` 启动。

## API 详细说明

### 1. 欢迎页面

**请求**:
```
GET /
```

**响应示例**:
```json
{
  "message": "欢迎使用AI算命应用"
}
```

### 2. 获取算命结果

**请求**:
```
POST /fortune
Content-Type: application/json

{
  "birth_date": "2000-01-01"
}
```

**参数说明**:
- `birth_date`: 出生年月日，格式为 YYYY-MM-DD

**响应示例**:
```json
{
  "fortune": "根据你的生辰八字分析，你是在千禧年出生的，具有很强的适应力和创新精神。命中有贵人相助，事业运势不错，但需要注意健康方面..."
}
```

### 3. 与算命先生对话

**请求**:
```
POST /chat
Content-Type: application/json

{
  "message": "我的事业运势如何？",
  "birth_date": "2000-01-01"
}
```

**参数说明**:
- `message`: 用户发送的消息
- `birth_date`: 出生年月日，格式为 YYYY-MM-DD

**响应示例**:
```json
{
  "fortune": "根据你的八字，事业方面有贵人相助，今年特别适合拓展人脉和寻找新的发展机会。但要注意避免急躁，稳扎稳打才能获得长期成功..."
}
```

## 使用 curl 测试 API

### 测试欢迎页面

```bash
curl -X GET http://127.0.0.1:8000/
```

### 获取算命结果

```bash
curl -X POST http://127.0.0.1:8000/fortune \
-H "Content-Type: application/json" \
-d '{"birth_date": "2000-01-01"}'
```

### 与算命先生对话

```bash
curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{"message": "我的事业运势如何？", "birth_date": "2000-01-01"}'
```

## 注意事项

1. 所有日期必须使用 `YYYY-MM-DD` 格式
2. API 调用需要确保 Azure OpenAI 服务正常配置
3. 对于同一个 `birth_date`，系统会维护对话历史记录，保持上下文连贯性
4. 响应时间可能因模型推理而有所延迟，请耐心等待
