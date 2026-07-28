"""
HTTP response headers module.

Fetches the target over HTTPS first, falling back to HTTP if TLS
isn't available. Returns the raw headers and status code — the
security_observations module is what interprets these headers for
missing protections, keeping "collect" and "analyze" as separate
responsibilities.
"""

import logging
from typing import Any, Dict

import requests

logger = logging.getLogger("reconkit")

REQUEST_TIMEOUT = 8
USER_AGENT = "reconkit/0.1 (authorized-recon-tool)"


def run(domain: str) -> Dict[str, Any]:
    headers = {"User-Agent": USER_AGENT}

    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}"
        try:
            logger.info(f"[http] Fetching {url}")
            resp = requests.get(
                url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True
            )
            return {
                "final_url": resp.url,
                "status_code": resp.status_code,
                "scheme_used": scheme,
                "headers": dict(resp.headers),
            }
        except requests.exceptions.SSLError as exc:
            logger.warning(f"[http] TLS error on {url}: {exc}")
            continue
        except requests.exceptions.RequestException as exc:
            logger.warning(f"[http] Request to {url} failed: {exc}")
            continue

    logger.error(f"[http] Both HTTPS and HTTP failed for {domain}")
    return {"error": "Target did not respond over HTTPS or HTTP"}
