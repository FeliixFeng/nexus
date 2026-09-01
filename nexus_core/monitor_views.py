import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings


def _bytes_to_gb(b):
    return round(b / (1024 ** 3), 1)


def _uptime_text(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    if days > 0:
        return f"{days}天 {hours}小时"
    minutes = (seconds % 3600) // 60
    return f"{hours}小时 {minutes}分"



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
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        data = resp.json()
        result["online"] = True
        result["hostname"] = data.get("hostname", name)
        result["platform"] = data.get("platform", "unknown")
        result["arch"] = data.get("arch", "")
        result["collected_at"] = data.get("collected_at", "")

        cpu = data.get("cpu", {})
        result["cpu_percent"] = cpu.get("percent", 0)
        result["cpu_count"] = cpu.get("count", 0)
        result["load_avg"] = cpu.get("load_avg", [0, 0, 0])

        mem = data.get("memory", {})
        result["mem_total"] = _bytes_to_gb(mem.get("total", 0))
        result["mem_used"] = _bytes_to_gb(mem.get("used", 0))
        result["mem_percent"] = mem.get("percent", 0)

        disk = data.get("disk", {})
        result["disk_total"] = _bytes_to_gb(disk.get("total", 0))
        result["disk_used"] = _bytes_to_gb(disk.get("used", 0))
        result["disk_percent"] = disk.get("percent", 0)

        result["uptime"] = _uptime_text(data.get("uptime_seconds", 0))


        bat = data.get("battery")
        if bat:
            result["battery"] = {
                "percent": round(bat.get("percent", 0), 1),
                "plugged": bat.get("power_plugged"),
            }

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
    """监控页面 — 先渲染骨架，数据异步加载"""
    server_names = [s["name"] for s in settings.MONITOR_SERVERS]
    return render(request, "nexus_core/monitor.html", {
        "server_names": server_names,
    })


def monitor_data(request):
    """API — 返回所有服务器数据 JSON（并行请求）"""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:
        servers = list(pool.map(_fetch_server, settings.MONITOR_SERVERS))

    total = len(servers)
    online = sum(1 for s in servers if s["online"])
    all_containers = []
    for s in servers:
        all_containers.extend(s.get("containers", []))

    return JsonResponse({
        "servers": servers,
        "total": total,
        "online": online,
        "containers_count": len(all_containers),
    })
