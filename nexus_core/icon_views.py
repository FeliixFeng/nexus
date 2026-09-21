import re

import requests
from django.http import Http404, HttpResponse

_HOST_RE = re.compile(r"^[a-zA-Z0-9.-]+(:\d+)?$")
_CACHE = {}
_CACHE_MAX = 200


def _valid_host(host: str) -> bool:
    return bool(host) and len(host) < 255 and bool(_HOST_RE.match(host))


def site_icon(request):
    """同源图标代理：GET /icon/?host=example.com"""
    host = (request.GET.get("host") or "").strip().lower()
    if not _valid_host(host):
        raise Http404

    cached = _CACHE.get(host)
    if cached is not None:
        if not cached:
            raise Http404
        data, ctype = cached
        return HttpResponse(data, content_type=ctype)

    candidates = [
        f"https://{host}/favicon.ico",
        f"https://{host}/apple-touch-icon.png",
        f"https://{host}/favicon.png",
    ]
    for url in candidates:
        try:
            resp = requests.get(
                url,
                timeout=4,
                allow_redirects=True,
                verify=False,
                headers={"User-Agent": "NexusIconProxy/1.0"},
            )
        except Exception:
            continue
        if resp.status_code != 200:
            continue
        body = resp.content or b""
        if not body or len(body) > 256_000:
            continue
        ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        looks_image = ctype.startswith("image/") or url.endswith((".ico", ".png"))
        if not looks_image:
            continue
        if not ctype.startswith("image/"):
            ctype = "image/x-icon" if url.endswith(".ico") else "image/png"
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.clear()
        _CACHE[host] = (body, ctype)
        return HttpResponse(body, content_type=ctype)

    if len(_CACHE) >= _CACHE_MAX:
        _CACHE.clear()
    _CACHE[host] = b""
    raise Http404
