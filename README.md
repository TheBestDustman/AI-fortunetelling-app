# AI-Fortunetelling-App

AI算命机器人，基于大语言模型的现代算命应用。用户输入出生年月日，AI返回算命结果，并支持后续交互式问答，探索更深层次的命运解析。

## 项目概述

本项目使用 Azure OpenAI 的 GPT-4o 模型，结合 LangGraph 框架构建了一个交互式算命应用。系统会根据用户提供的生辰八字（出生年月日）生成个性化的性格特点和运势分析，并支持后续的对话式交互。项目同时提供命令行交互界面和FastAPI网络接口两种使用方式。

## 环境要求

- **Python**: 3.12.2
- **包管理器**: Conda (必须使用 Conda)
- **核心依赖**: 
  - langchain
  - langgraph
  - azure-openai
  - loguru

## 快速开始

### 1. 环境安装

**推荐使用 Conda 来管理环境**，支持多种安装方式：

#### 使用 environment.yml

```bash
# 克隆项目
git clone <repository-url>
cd AI-Fortunetelling-App

# 使用 environment.yml 创建 conda 环境
conda env create -f environment.yml

# 激活环境
conda activate first_seed

# 安装项目包（开发模式）
pip install -e .
```

### 2. 环境变量配置

项目需要设置以下环境变量：

```bash
# Windows
set AZURE_OPENAI_ENDPOINT=your_endpoint_here
set AZURE_OPENAI_API_KEY=your_api_key_here

# Linux/macOS
export AZURE_OPENAI_ENDPOINT=your_endpoint_here
export AZURE_OPENAI_API_KEY=your_api_key_here
```

或者，你可以创建一个 `.env` 文件在项目根目录下。

### 3. VS Code 配置

如果使用 VS Code 进行开发：

1. 打开命令面板 (`Ctrl+Shift+P` 或 `Cmd+Shift+P`)
2. 选择 `Python: Select Interpreter`
3. 选择你的 conda 环境路径

### 4. 运行方法

#### 命令行交互模式

```bash
# 使用 make 命令运行
make run

# 或者直接运行 Python 脚本
python src/ai_fortunetelling_app/chat_services/AI_Fortunetelling.py
```

按照终端提示操作：
1. 输入出生年月日（格式: YYYY-MM-DD）
2. 获取 AI 生成的算命结果
3. 继续提问或输入"退出"、"q"或"quit"结束对话

#### FastAPI 接口模式

启动 FastAPI 服务：

```bash
# 运行 FastAPI 应用
python app.py
```

服务启动后，可通过以下方式访问：

- Web界面：访问 http://127.0.0.1:8000/docs 使用交互式 API 文档
- API 端点：
  - GET `/` - 欢迎页面
  - POST `/fortune` - 获取算命结果
  - POST `/chat` - 与算命先生进行对话

## 项目结构

```
AI-Fortunetelling-App/
├── src/
│   └── ai_fortunetelling_app/
│       └── chat_services/
│           ├── AI_Fortunetelling.py  # 主程序（命令行模式）
│           ├── fortune_service.py    # 算命核心服务
│           └── app.py               # FastAPI接口
├── tests/                            # 测试目录
├── docs/                             # 文档目录
├── environment.yml                   # Conda 环境配置
├── requirements.txt                  # 依赖包列表
├── Makefile                          # 项目管理命令
└── README.md                         # 项目说明
```

## 功能特点

- **生辰八字分析**: 根据用户出生年月日进行性格和运势分析
- **对话式交互**: 支持后续追问，进一步探索运势细节
- **流式响应**: 使用 LangGraph 流式处理 AI 响应
- **健壮错误处理**: 完善的异常捕获和日志记录
- **双重接口**: 提供命令行交互和 RESTful API 两种使用方式
- **OpenAPI 文档**: 自动生成的 API 文档，便于开发者理解和测试

## 开发指南

### 安装开发依赖

```bash
pip install -r requirements-dev.txt
```

### 代码格式化和检查

```bash
# 代码格式化
make format

# 代码检查
make lint
```

### 运行测试

```bash
make test
```

## 注意事项

- 此算命机器人需要"AZURE_OPENAI_ENDPOINT"和"AZURE_OPENAI_API_KEY"，这两项为连接GPT-4o的必要密钥，需自行在环境变量中设置
- 应用中的算命结果仅供娱乐，不应作为实际决策依据
- 请遵守 Azure OpenAI 服务使用条款和相关法律法规
- 使用 FastAPI 模式时，默认服务运行在 http://127.0.0.1:8000，可通过修改代码更改端口
- 在生产环境中部署 FastAPI 服务时，建议配置适当的 CORS 策略和安全措施

## 许可证

[添加你的许可证信息]

## 贡献指南

欢迎提交 Issues 和 Pull Requests 来改进这个项目。