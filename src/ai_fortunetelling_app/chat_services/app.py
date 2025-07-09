from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger
from pydantic import BaseModel
from datetime import datetime

# 导入我们的核心服务
import fortune_service

############################################################################################################
# 定义API数据模型
class UserInput(BaseModel):
    birth_date: str  # 出生年月日，格式为 YYYY-MM-DD

    def validate_birth_date(self):
        """验证出生日期格式是否正确"""
        try:
            datetime.strptime(self.birth_date, "%Y-%m-%d")
            return True
        except ValueError:
            raise ValueError("出生年月日格式错误，应为 YYYY-MM-DD")

class FortuneResponse(BaseModel):
    fortune: str

class ChatRequest(BaseModel):
    message: str
    birth_date: str

############################################################################################################
# 创建FastAPI应用
app = FastAPI(
    title="AI算命应用",
    description="基于生辰八字的AI算命应用API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "欢迎使用AI算命应用"}

@app.post("/fortune", response_model=FortuneResponse)
async def get_fortune(user_input: UserInput):
    try:
        # 验证出生日期格式
        if not user_input.validate_birth_date():
            raise HTTPException(status_code=400, detail="出生年月日格式错误，应为 YYYY-MM-DD")
        
        # 调用核心服务获取算命结果
        fortune_result = fortune_service.get_fortune(user_input.birth_date)
        
        return FortuneResponse(fortune=fortune_result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"生成算命结果时出错: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@app.post("/chat", response_model=FortuneResponse)
async def chat(chat_request: ChatRequest):
    try:
        # 验证出生日期格式
        user_input = UserInput(birth_date=chat_request.birth_date)
        if not user_input.validate_birth_date():
            raise HTTPException(status_code=400, detail="出生年月日格式错误，应为 YYYY-MM-DD")
        
        # 调用核心服务获取聊天回复
        chat_result = fortune_service.chat_with_fortune_teller(
            chat_request.birth_date, 
            chat_request.message
        )
        
        return FortuneResponse(fortune=chat_result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"生成聊天回复时出错: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

# 启动服务器
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)