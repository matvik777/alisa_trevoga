from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

PROXY_LIST_URL = "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_ru.txt"
CACHE_PATH = Path(__file__).resolve().parent.parent / "state" / "mtproxy_cache.json"


def load_mtproxies(limit: int = 10) -> list[tuple[str, int, str]]:
    response = requests.get(PROXY_LIST_URL, timeout=20)
    response.raise_for_status()

    proxies: list[tuple[str, int, str]] = []

    for raw_line in response.text.splitlines():
        line = raw_line.strip()
        if not line or not line.startswith("tg://proxy?"):
            continue

        parsed = urlparse(line)
        params = parse_qs(parsed.query)

        host = params.get("server", [None])[0]
        port = params.get("port", [None])[0]
        secret = params.get("secret", [None])[0]

        if not host or not port or not secret:
            continue

        try:
            proxies.append((host, int(port), secret))
        except ValueError:
            continue

        if len(proxies) >= limit:
            break

    return proxies


def load_cached_proxy() -> tuple[str, int, str] | None:
    if not CACHE_PATH.exists():
        return None

    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        host = data.get("host")
        port = int(data.get("port"))
        secret = data.get("secret")
        if host and port and secret:
            return host, port, secret
    except Exception:
        return None

    return None


def save_cached_proxy(host: str, port: int, secret: str) -> None:
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {
                "host": host,
                "port": port,
                "secret": secret,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )