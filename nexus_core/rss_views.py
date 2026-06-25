import time
import json
import urllib.request
from datetime import datetime, timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

# RSS 源配置
RSS_FEEDS = getattr(settings, 'RSS_FEEDS', [])
RSS_PROXY_URL = getattr(settings, 'RSS_PROXY_URL', '')

# 内存缓存
_cache = {}
CACHE_TTL = 1800  # 30分钟


def _fetch_from_proxy():
    """从 Lunar 代理服务器获取 RSS 数据"""
    if not RSS_PROXY_URL:
        return None

    cache_key = 'rss_proxy_all'
    cached = _cache.get(cache_key)
    if cached and time.time() - cached['time'] < CACHE_TTL:
        return cached['data']

    try:
        url = f"{RSS_PROXY_URL}/rss"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        # 转换格式，匹配前端期望的结构
        results = []
        feed_color_map = {f['name']: f.get('color', '#6366f1') for f in RSS_FEEDS}

        for feed in data.get('feeds', []):
            entries = []
            for e in feed.get('entries', []):
                published = None
                ts = 0
                pub_str = e.get('published', '')
                if pub_str:
                    try:
                        # 尝试解析各种时间格式
                        for fmt in ('%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S',
                                    '%a, %d %b %Y %H:%M:%S GMT', '%Y-%m-%dT%H:%M:%S.%f'):
                            try:
                                published = datetime.strptime(pub_str, fmt)
                                if published.tzinfo is None:
                                    published = published.replace(tzinfo=timezone.utc)
                                ts = published.timestamp()
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass

                # 清理 HTML 标签
                import re
                summary = re.sub(r'<[^>]+>', '', e.get('summary', ''))[:200]

                entries.append({
                    'title': e.get('title', '无标题'),
                    'link': e.get('link', '#'),
                    'summary': summary,
                    'published': published.isoformat() if published else None,
                    'timestamp': ts,
                })

            result = {
                'name': feed['name'],
                'icon': feed.get('icon', '📰'),
                'color': feed_color_map.get(feed['name'], '#6366f1'),
                'entries': entries,
                'ok': feed.get('ok', True),
            }
            results.append(result)

        _cache[cache_key] = {'time': time.time(), 'data': results}
        return results

    except Exception as e:
        print(f"[RSS Proxy] 代理请求失败: {e}")
        return None


def _fetch_feed_local(feed_config):
    """本地抓取单个 RSS 源（备用方案）"""
    import feedparser
    import hashlib

    url = feed_config['url']
    cache_key = 'rss_' + hashlib.md5(url.encode()).hexdigest()

    cached = _cache.get(cache_key)
    if cached and time.time() - cached['time'] < CACHE_TTL:
        return cached['data']

    _HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NexusRSS/1.0)'}

    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        resp = urllib.request.urlopen(req, timeout=8)
        raw = resp.read()
        d = feedparser.parse(raw)
        entries = []
        for entry in d.entries[:20]:
            published = None
            for attr in ('published_parsed', 'updated_parsed'):
                t = getattr(entry, attr, None)
                if t:
                    try:
                        published = datetime(*t[:6], tzinfo=timezone.utc)
                    except Exception:
                        pass
                    break

            import re
            summary = ''
            if hasattr(entry, 'summary'):
                summary = re.sub(r'<[^>]+>', '', entry.summary)[:200]

            entries.append({
                'title': getattr(entry, 'title', '无标题'),
                'link': getattr(entry, 'link', '#'),
                'summary': summary,
                'published': published.isoformat() if published else None,
                'timestamp': published.timestamp() if published else 0,
            })

        result = {
            'name': feed_config['name'],
            'icon': feed_config.get('icon', '📰'),
            'color': feed_config.get('color', '#6366f1'),
            'entries': entries,
            'ok': True,
        }
    except Exception as e:
        result = {
            'name': feed_config['name'],
            'icon': feed_config.get('icon', '📰'),
            'color': feed_config.get('color', '#6366f1'),
            'entries': [],
            'ok': False,
            'error': str(e),
        }

    _cache[cache_key] = {'time': time.time(), 'data': result}
    return result


def rss_page(request):
    """RSS 阅读器页面"""
    return render(request, 'nexus_core/rss.html', {
        'feeds': RSS_FEEDS,
    })


def rss_data(request):
    """API：返回所有 RSS 源数据"""
    source = request.GET.get('source', '')

    # 优先走代理，失败则本地抓取
    proxy_results = _fetch_from_proxy()

    if proxy_results is not None:
        results = proxy_results
    else:
        results = []
        for feed in RSS_FEEDS:
            if source and feed['name'] != source:
                continue
            data = _fetch_feed_local(feed)
            results.append(data)

    # 按时间排序合并所有条目
    all_entries = []
    for r in results:
        if source and r['name'] != source:
            continue
        for e in r['entries']:
            e['source'] = r['name']
            e['source_icon'] = r['icon']
            e['source_color'] = r['color']
            all_entries.append(e)

    all_entries.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    return JsonResponse({
        'feeds': results,
        'all': all_entries[:100],
    })
