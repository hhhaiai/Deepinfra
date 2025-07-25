import asyncio
import httpx
import time
from typing import List, Dict, Any

# API配置
API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/event-stream",
    "Content-Type": "application/json",
    "X-Deepinfra-Source": "web-page",
    "Origin": "https://deepinfra.com",
    "Referer": "https://deepinfra.com/"
}

# 三个模型轮流使用
MODELS = [
    "deepseek-ai/DeepSeek-R1-0528-Turbo",
    "deepseek-ai/DeepSeek-V3-0324-Turbo", 
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
]

def get_payload(request_id: int) -> dict:
    """根据请求ID轮流选择模型"""
    model = MODELS[(request_id - 1) % len(MODELS)]
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ],
        "stream": False
    }

async def make_single_request(session: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
    """发送单个请求"""
    try:
        payload = get_payload(request_id)
        start_time = time.time()
        response = await session.post(API_URL, json=payload, headers=HEADERS)
        end_time = time.time()
        
        return {
            "id": request_id,
            "model": payload["model"],
            "status_code": response.status_code,
            "response_time": round(end_time - start_time, 3),
            "success": response.status_code == 200,
            "content_length": len(response.text) if response.status_code == 200 else 0,
            "error": None if response.status_code == 200 else response.text[:100]
        }
    except Exception as e:
        return {
            "id": request_id,
            "model": get_payload(request_id)["model"],
            "status_code": 0,
            "response_time": 0,
            "success": False,
            "content_length": 0,
            "error": str(e)[:100]
        }

async def run_batch_requests(batch_size: int = 50) -> List[Dict[str, Any]]:
    """批量发送请求"""
    results = []
    total_requests = 1000
    
    print(f"开始发送 {total_requests} 个请求，批次大小: {batch_size}")
    
    async with httpx.AsyncClient(timeout=30.0) as session:
        for batch_start in range(0, total_requests, batch_size):
            batch_end = min(batch_start + batch_size, total_requests)
            batch_tasks = []
            
            print(f"处理批次 {batch_start + 1}-{batch_end}...")
            
            # 创建当前批次的任务
            for i in range(batch_start, batch_end):
                task = make_single_request(session, i + 1)
                batch_tasks.append(task)
            
            # 并发执行当前批次
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # 处理结果
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append({
                        "id": len(results) + 1,
                        "status_code": 0,
                        "response_time": 0,
                        "success": False,
                        "content_length": 0,
                        "error": str(result)[:100]
                    })
                else:
                    results.append(result)
            
            # 显示进度
            success_count = sum(1 for r in results if r["success"])
            print(f"已完成: {len(results)}/{total_requests}, 成功: {success_count}")
            
            # 批次间短暂延迟，避免过载
            if batch_end < total_requests:
                await asyncio.sleep(0.1)
    
    return results

def analyze_results(results: List[Dict[str, Any]]):
    """分析结果统计"""
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total - successful
    
    if successful > 0:
        response_times = [r["response_time"] for r in results if r["success"]]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    # 统计状态码
    status_codes = {}
    for r in results:
        code = r["status_code"]
        status_codes[code] = status_codes.get(code, 0) + 1
    
    # 按模型统计
    model_stats = {}
    for r in results:
        model = r.get("model", "unknown")
        if model not in model_stats:
            model_stats[model] = {"total": 0, "success": 0, "failed": 0}
        model_stats[model]["total"] += 1
        if r["success"]:
            model_stats[model]["success"] += 1
        else:
            model_stats[model]["failed"] += 1
    
    print("\n" + "="*50)
    print("测试结果统计")
    print("="*50)
    print(f"总请求数: {total}")
    print(f"成功请求: {successful} ({successful/total*100:.1f}%)")
    print(f"失败请求: {failed} ({failed/total*100:.1f}%)")
    print(f"平均响应时间: {avg_response_time:.3f}s")
    print(f"最快响应时间: {min_response_time:.3f}s")
    print(f"最慢响应时间: {max_response_time:.3f}s")
    
    print("\n各模型统计:")
    for model, stats in model_stats.items():
        success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {model}:")
        print(f"    总数: {stats['total']}, 成功: {stats['success']}, 失败: {stats['failed']}")
        print(f"    成功率: {success_rate:.1f}%")
    
    print("\n状态码分布:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count} 次")
    
    # 显示前几个错误
    errors = [r for r in results if not r["success"] and r["error"]]
    if errors:
        print(f"\n前5个错误示例:")
        for i, error in enumerate(errors[:5], 1):
            print(f"  {i}. 请求#{error['id']} ({error.get('model', 'unknown')}): {error['error']}")

async def main():
    """主函数"""
    print("DeepInfra API 压力测试 - 1000次请求")
    print("-" * 40)
    
    start_time = time.time()
    results = await run_batch_requests(batch_size=50)
    end_time = time.time()
    
    total_time = end_time - start_time
    print(f"\n总耗时: {total_time:.2f}秒")
    print(f"平均QPS: {len(results)/total_time:.2f} 请求/秒")
    
    analyze_results(results)
    
    # 保存详细结果到文件
    import json
    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_requests": len(results),
                "successful_requests": sum(1 for r in results if r["success"]),
                "total_time": total_time,
                "average_qps": len(results)/total_time
            },
            "details": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: api_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())