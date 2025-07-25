
## 原地址

- https://deepinfra.com/dash/api_keys
- 9G3r5A9S80nLsmR8zQAiD0Vp5xNXn0dN


``` shell

# 无token 流式回复

curl -X POST "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "X-Deepinfra-Source: web-page" \
  -H "Origin: https://deepinfra.com" \
  -H "Referer: https://deepinfra.com/" \
  -d '{
    "model": "deepseek-ai/DeepSeek-R1-0528-Turbo",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "stream": true
  }'

### 无token 非流式回复

curl -X POST "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "X-Deepinfra-Source: web-page" \
  -H "Origin: https://deepinfra.com" \
  -H "Referer: https://deepinfra.com/" \
  -d '{
    "model": "deepseek-ai/DeepSeek-R1-0528-Turbo",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "stream": false
  }'

# token 是可选项    -H "Authorization: Bearer $TOKEN" \

```


## 本地



``` shell

# 获取本地模型


# 聊天完成请求

curl -X POST "http://0.0.0.0:8000/v1/chat/completions" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "X-Deepinfra-Source: web-page" \
  -H "Origin: https://deepinfra.com" \
  -H "Referer: https://deepinfra.com/" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3-0324-Turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user", 
        "content": "Explain quantum computing in simple terms."
      }
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": true
  }'




curl -X POST "http://0.0.0.0:8000/v1/chat/completions" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "X-Deepinfra-Source: web-page" \
  -H "Origin: https://deepinfra.com" \
  -H "Referer: https://deepinfra.com/" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3-0324-Turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user", 
        "content": "Explain quantum computing in simple terms."
      }
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": false
  }'



```