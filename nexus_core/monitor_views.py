import time
import requests
from django.shortcuts import render
from django.conf import settings


def _bytes_to_gb(b):
    return round(b / (1024 ** 3), 1)


def _bytes_to_mb(b):
    return round(b / (1024 ** 2), 1)


def _uptime_text(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    if days > 0:
        return f"{days}天 {hours}小时"
    minutes = (seconds % 3600) // 60
    return f"{hours}小时 {minutes}分"


def _format_net_traffic(bytes_val):
    gb = bytes_val / (1024 ** 3)
    if gb >= 1:
        return f"{gb:.1f} GB"
    mb = bytes_val / (1024 ** 2)
    return f"{mb:.0f} MB"


def _fetch_server(server_cfg):
    """拉取单台服务器数据，失败返回离线状态"""
    name = server_cfg["name"]
    url = server_cfg["url"]
    role = server_cfg.get("role", "")
    result = {
        "name": name,
        "role": role,
        "online": False,
        "error": None,
    }
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        result["online"] = True
        result["hostname"] = data.get("hostname", name)
        result["platform"] = data.get("platform", "unknown")
        result["arch"] = data.get("arch", "")
        result["collected_at"] = data.get("collected_at", "")

        # CPU
        cpu = data.get("cpu", {})
        result["cpu_percent"] = cpu.get("percent", 0)
        result["cpu_count"] = cpu.get("count", 0)
        result["load_avg"] = cpu.get("load_avg", [0, 0, 0])

        # Memory
        mem = data.get("memory", {})
        result["mem_total"] = _bytes_to_gb(mem.get("total", 0))
        result["mem_used"] = _bytes_to_gb(mem.get("used", 0))
        result["mem_percent"] = mem.get("percent", 0)

        # Disk
        disk = data.get("disk", {})
        result["disk_total"] = _bytes_to_gb(disk.get("total", 0))
        result["disk_used"] = _bytes_to_gb(disk.get("used", 0))
        result["disk_percent"] = disk.get("percent", 0)

        # Uptime
        result["uptime"] = _uptime_text(data.get("uptime_seconds", 0))

        # Network
        net = data.get("network", {})
        result["net_sent"] = _format_net_traffic(net.get("bytes_sent", 0))
        result["net_recv"] = _format_net_traffic(net.get("bytes_recv", 0))

        # Battery
        bat = data.get("battery")
        if bat:
            result["battery"] = {
                "percent": bat.get("percent", 0),
                "plugged": bat.get("power_plugged"),
                "remaining": bat.get("remaining_text", ""),
            }

        # Docker
        docker = data.get("docker")
        if docker:
            result["containers"] = docker
            result["containers_total"] = len(docker)
            running = sum(1 for c in docker if c.get("status", "").startswith("Up"))
            result["containers_running"] = running

    except requests.Timeout:
        result["error"] = "连接超时"
    except requests.ConnectionError:
        result["error"] = "无法连接"
    except Exception as e:
        result["error"] = str(e)[:80]

    return result


def monitor(request):
    """服务器监控页面"""
    servers = []
    for cfg in settings.MONITOR_SERVERS:
        servers.append(_fetch_server(cfg))

    # 汇总
    total = len(servers)
    online = sum(1 for s in servers if s["online"])
    all_containers = []
    for s in servers:
        all_containers.extend(s.get("containers", []))

    context = {
        "servers": servers,
        "total": total,
        "online": online,
        "all_containers": all_containers,
    }
    return render(request, "core/monitor.html", context)
