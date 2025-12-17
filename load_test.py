#!/usr/bin/env python3
"""
简单压力测试脚本（并发请求提交任务到 /tasks/submit）

用法示例:
  python load_test.py --url http://localhost:8000 --concurrency 20 --requests 100

脚本会并发上传小文本文件并使用唯一的 task_name 触发任务。
"""
import argparse
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


def submit_task(session, base_url, content, task_name):
    url = f"{base_url.rstrip('/')}/tasks/submit"
    files = {"file": ("params.txt", content, "text/plain")}
    data = {"task_name": task_name}
    start = time.time()
    try:
        r = session.post(url, files=files, data=data, timeout=30)
        latency = time.time() - start
        return {
            "ok": r.status_code == 200,
            "status_code": r.status_code,
            "text": r.text,
            "latency": latency,
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "latency": time.time() - start}


def main():
    parser = argparse.ArgumentParser(description="Simple load test for Celery Demo API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of API")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent workers")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests to send")
    parser.add_argument("--content", default="param=1", help="Content of uploaded params.txt")
    args = parser.parse_args()

    total = args.requests
    concurrency = max(1, args.concurrency)

    print(f"Target: {args.url}/tasks/submit | total requests: {total} | concurrency: {concurrency}")

    session = requests.Session()

    successes = 0
    failures = 0
    latencies = []

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []
        for i in range(total):
            # 生成唯一 task_name，避免重复冲突
            task_name = f"loadtest-{int(time.time())}-{uuid.uuid4().hex[:8]}-{i}"
            futures.append(ex.submit(submit_task, session, args.url, args.content, task_name))

        for fut in as_completed(futures):
            res = fut.result()
            if res.get("ok"):
                successes += 1
                latencies.append(res.get("latency", 0))
            else:
                failures += 1

    print("\n=== Summary ===")
    print(f"Total: {total}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    if latencies:
        print(f"Avg latency: {sum(latencies)/len(latencies):.3f}s")
        print(f"Min latency: {min(latencies):.3f}s")
        print(f"Max latency: {max(latencies):.3f}s")


if __name__ == "__main__":
    main()
