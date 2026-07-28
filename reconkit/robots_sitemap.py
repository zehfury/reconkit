"""
robots.txt / sitemap.xml module.

Both files are optional by spec — a 404 here is a normal result,
not an error, so it's recorded as "not found" rather than logged
as a failure. Only connection-level problems (timeout, DNS, TLS)
are treated as warnings.
"""

import logging
from typing import Any, Dict

import requests

logger = logging.getLogger("reconkit")

REQUEST_TIMEOUT = 8
USER_AGENT = "reconkit/0.1 (authorized-recon-tool)"
MAX_CHARS = 3000  # cap stored content so a huge sitemap doesn't bloat the report


def _fetch(url: str) -> Dict[str, Any]:
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            content = resp.text[:MAX_CHARS]
            truncated = len(resp.text) > MAX_CHARS
            return {"found": True, "status_code": 200, "content": content, "truncated": truncated}
        return {"found": False, "status_code": resp.status_code}
    except requests.exceptions.RequestException as exc:
        logger.warning(f"[robots_sitemap] Request to {url} failed: {exc}")
        return {"found": False, "error": str(exc)}


def run(domain: str) -> Dict[str, Any]:
    logger.info(f"[robots_sitemap] Checking robots.txt and sitemap.xml for {domain}")
    base = f"https://{domain}"
    result = {
        "robots_txt": _fetch(f"{base}/robots.txt"),
        "sitemap_xml": _fetch(f"{base}/sitemap.xml"),
    }
    logger.info(
        f"[robots_sitemap] robots.txt found={result['robots_txt'].get('found')}, "
        f"sitemap.xml found={result['sitemap_xml'].get('found')}"
    )
    return result
