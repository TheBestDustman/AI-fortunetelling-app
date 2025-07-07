# AI-Fortunetelling-App

AI算命机器人，用户输入出生年月日，AI返回算命结果，可根据需要继续询问相关问题

## 环境要求

- **Python**: 3.12.2
- **包管理器**: Conda (必须使用 Conda)

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

### 2. VS Code 配置

如果使用 VS Code 进行开发：

1. 打开命令面板 (`Cmd+Shift+P`)
2. 选择 `Python: Select Interpreter`
3. 选择 conda 环境路径：`/Users/your-username/anaconda3/envs/first_seed/bin/python`


### 3. 运行方法

直接运行chat_azure_openai_gpt_4o_graph.py
根据终端提示输入出生年月日并按下回车，AI会返回算命结果
后续可根据需要继续向AI提问
输入“退出，q，quit”退出算命程序

### 注意事项

此算命机器人需要“AZURE_OPENAI_ENDPOINT”和“AZURE_OPENAI_API_KEY”
这两项为连接gpt4o的必要key，需自行在环境变量中设置