#!/usr/bin/env python3
"""
Nexus Monitor Agent — 轻量服务器监控探针
每台机器部署一份，暴露 HTTP :9100 返回 JSON 系统指标。
用法: python3 monitor_agent.py [--port 9100]
"""
import json
import time
import argparse
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

try:
    import psutil
except ImportError:
    print("需要 psutil: pip install psutil")
    exit(1)


def collect_metrics():
    """采集系统指标"""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    load_avg = [round(x, 2) for x in psutil.getloadavg()]

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    net = psutil.net_io_counters()
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    data = {
        "hostname": platform.node(),
        "platform": platform.system().lower(),  # linux / darwin
        "arch": platform.machine(),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "load_avg": load_avg,
        },
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": mem.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
        },
    }

    # 电池信息（笔记本 / Mac）
    battery = psutil.sensors_battery()
    if battery:
        secs = battery.secsleft
        if secs == psutil.POWER_TIME_UNLIMITED:
            remaining = "充电中"
        elif secs == psutil.POWER_TIME_UNKNOWN:
            remaining = "未知"
        else:
            h, m = divmod(secs // 60, 60)
            remaining = f"{h}h{m}m" if h else f"{m}m"
        data["battery"] = {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft,
            "remaining_text": remaining,
        }

    # Docker 容器（可选，有 docker 则采集）
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            containers = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    containers.append({
                        "name": parts[0],
                        "status": parts[1],
                        "image": parts[2] if len(parts) > 2 else "",
                    })
            data["docker"] = containers
    except Exception:
        pass

    return data


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            data = collect_metrics()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # 静默日志


def main():
    parser = argparse.ArgumentParser(description="Nexus Monitor Agent")
    parser.add_argument("--port", type=int, default=9100, help="监听端口")
    parser.add_argument("--bind", default="0.0.0.0", help="绑定地址")
    args = parser.parse_args()

    server = HTTPServer((args.bind, args.port), MetricsHandler)
    print(f"Monitor Agent running on {args.bind}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
