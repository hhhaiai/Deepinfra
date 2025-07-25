import json
import os
from typing import Dict, Any
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模型列表
MODELS = {
    "object": "list",
    "data": [
        {"id": "deepseek-ai/DeepSeek-R1-0528-Turbo", "object": "model", "created": 1624980000, "owned_by": "deepseek-ai"},
        {"id": "deepseek-ai/DeepSeek-V3-0324-Turbo", "object": "model", "created": 1632000000, "owned_by": "deepseek-ai"},
        {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "object": "model", "created": 1640000000, "owned_by": "deepseek-ai"}
    ]
}

# 请求头模板
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/event-stream",
    "Content-Type": "application/json",
    "X-Deepinfra-Source": "web-page",
    "Origin": "https://deepinfra.com",
    "Referer": "https://deepinfra.com/"
}

def verify_token(request: Request):
    # """验证token"""
    # token = os.getenv("TOKEN")
    # if not token:
    #     return True
    
    # auth_header = request.headers.get("authorization")
    # if not auth_header or auth_header != f"Bearer {token}":
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.get("/v1/models")
async def get_models(request: Request):
    """获取模型列表"""
    verify_token(request)
    return MODELS

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """代理聊天完成请求"""
    verify_token(request)
    
    try:
        body = await request.json()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepinfra.com/v1/openai/chat/completions",
                json=body,
                headers=HEADERS
            )
            
            return StreamingResponse(
                response.aiter_bytes(),
                status_code=response.status_code,
                headers={"Content-Type": response.headers.get("Content-Type", "application/json")}
            )
            
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)