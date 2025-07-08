# AI-Fortunetelling-App

AI算命机器人，基于大语言模型的现代算命应用。用户输入出生年月日，AI返回算命结果，并支持后续交互式问答，探索更深层次的命运解析。

## 项目概述

本项目使用 Azure OpenAI 的 GPT-4o 模型，结合 LangGraph 框架构建了一个交互式算命应用。系统会根据用户提供的生辰八字（出生年月日）生成个性化的性格特点和运势分析。

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

## 项目结构

```
AI-Fortunetelling-App/
├── src/
│   └── ai_fortunetelling_app/
│       └── chat_services/
│           └── AI_Fortunetelling.py  # 主程序
├── tests/                            # 测试目录
├── docs/                             # 文档目录
├── environment.yml                   # Conda 环境配置
├── Makefile                          # 项目管理命令
└── README.md                         # 项目说明
```

## 功能特点

- **生辰八字分析**: 根据用户出生年月日进行性格和运势分析
- **对话式交互**: 支持后续追问，进一步探索运势细节
- **流式响应**: 使用 LangGraph 流式处理 AI 响应
- **健壮错误处理**: 完善的异常捕获和日志记录

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

## 许可证

[添加你的许可证信息]

## 贡献指南

欢迎提交 Issues 和 Pull Requests 来改进这个项目。