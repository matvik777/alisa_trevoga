from __future__ import annotations

from urllib.parse import urlparse, parse_qs

import requests

PROXY_LIST_URL = "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_ru.txt"


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