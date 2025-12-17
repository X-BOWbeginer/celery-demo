#!/usr/bin/env python3
"""
循环运行 `load_test.py` 的守护脚本，直到被中断。

示例:
  python run_load_test_forever.py --interval 2 --load-args "--concurrency 5 --requests 50 --url http://localhost:8000"

参数:
  --interval: 每次运行之间的等待秒数（默认 1）
  --load-args: 传递给 `load_test.py` 的参数字符串
  --max-runs: 可选，最多运行次数，0 或不设置表示无限
"""
import argparse
import shlex
import subprocess
import time
import sys


def main():
    parser = argparse.ArgumentParser(description="Run load_test.py repeatedly until interrupted")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds to wait between runs")
    parser.add_argument("--load-args", type=str, default="", help="Arguments to pass to load_test.py (quoted) e.g. '--concurrency 10 --requests 100'")
    parser.add_argument("--max-runs", type=int, default=0, help="Max number of runs (0 means infinite)")
    args = parser.parse_args()

    load_script = "./load_test.py"
    py = sys.executable or "python3"
    run_count = 0

    print(f"Starting endless runner: calling {load_script} with args: {args.load_args!r}")
    try:
        while True:
            if args.max_runs and run_count >= args.max_runs:
                print(f"Reached max runs ({args.max_runs}). Exiting.")
                break

            cmd = [py, load_script]
            if args.load_args:
                cmd += shlex.split(args.load_args)

            run_count += 1
            print(f"\n--- Run #{run_count} at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")

            try:
                # Run load_test.py and stream its output to the console
                proc = subprocess.run(cmd)
            except Exception as e:
                print(f"Error running load_test.py: {e}")

            if args.interval > 0:
                try:
                    time.sleep(args.interval)
                except KeyboardInterrupt:
                    print("Interrupted during sleep. Exiting.")
                    break

    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Exiting gracefuly...")


if __name__ == "__main__":
    main()
