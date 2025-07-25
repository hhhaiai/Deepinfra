import asyncio
import httpx
import time

async def test_api():
    """简单版本：调用API 1000次，三个模型轮流使用"""
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "X-Deepinfra-Source": "web-page",
        "Origin": "https://deepinfra.com",
        "Referer": "https://deepinfra.com/"
    }
    
    # 三个模型轮流使用
    models = [
        "deepseek-ai/DeepSeek-R1-0528-Turbo",
        "deepseek-ai/DeepSeek-V3-0324-Turbo", 
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
    ]
    
    def get_payload(request_id):
        return {
            "model": models[(request_id - 1) % len(models)],
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "stream": False
        }
    
    success_count = 0
    error_count = 0
    model_stats = {model: {"success": 0, "error": 0} for model in models}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = []
        payloads = []
        
        # 创建1000个请求任务，每个使用不同的模型
        for i in range(1000):
            payload = get_payload(i + 1)
            payloads.append(payload)
            task = client.post(url, json=payload, headers=headers)
            tasks.append(task)
        
        print("开始发送1000个请求（三个模型轮流使用）...")
        print(f"模型分布: 每个模型约 {1000//3} 个请求")
        start_time = time.time()
        
        # 并发执行所有请求
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # 统计结果
        for i, response in enumerate(responses, 1):
            model = payloads[i-1]["model"]
            
            if isinstance(response, Exception):
                error_count += 1
                model_stats[model]["error"] += 1
                if i <= 10:  # 只打印前10个错误
                    print(f"请求 {i} ({model}) 失败: {response}")
            else:
                if response.status_code == 200:
                    success_count += 1
                    model_stats[model]["success"] += 1
                else:
                    error_count += 1
                    model_stats[model]["error"] += 1
                    if error_count <= 10:  # 只打印前10个HTTP错误
                        print(f"请求 {i} ({model}) HTTP错误: {response.status_code}")
            
            # 每100个请求显示一次进度
            if i % 100 == 0:
                print(f"已完成: {i}/1000")
    
    total_time = end_time - start_time
    print(f"\n测试完成!")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"成功: {success_count}")
    print(f"失败: {error_count}")
    print(f"成功率: {success_count/1000*100:.1f}%")
    print(f"平均QPS: {1000/total_time:.2f}")
    
    print(f"\n各模型统计:")
    for model, stats in model_stats.items():
        total_model = stats["success"] + stats["error"]
        success_rate = stats["success"] / total_model * 100 if total_model > 0 else 0
        print(f"  {model.split('/')[-1]}:")
        print(f"    总数: {total_model}, 成功: {stats['success']}, 失败: {stats['error']}")
        print(f"    成功率: {success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_api())