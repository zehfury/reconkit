"""
IP + geolocation module.

Resolves the domain to an IPv4 address, then queries ip-api.com's
free endpoint for coarse geolocation (country, region, city, ISP).
Geolocation from IP is approximate by nature (often resolves to a
CDN or hosting provider's location, not the organization's real
address) — this is noted in the report, not just this docstring.
"""

import logging
import socket
from typing import Any, Dict

import requests

logger = logging.getLogger("reconkit")

GEO_API_URL = "http://ip-api.com/json/{ip}"
REQUEST_TIMEOUT = 5


def run(domain: str) -> Dict[str, Any]:
    logger.info(f"[ip] Resolving IP address for {domain}")
    try:
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror as exc:
        logger.error(f"[ip] Could not resolve {domain}: {exc}")
        return {"error": f"DNS resolution failed: {exc}"}

    result: Dict[str, Any] = {"ip_address": ip_address}

    try:
        resp = requests.get(GEO_API_URL.format(ip=ip_address), timeout=REQUEST_TIMEOUT)
        data = resp.json()
        if data.get("status") == "success":
            result.update({
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as"),
            })
        else:
            logger.warning(f"[ip] Geolocation lookup returned no data for {ip_address}")
            result["geolocation_error"] = data.get("message", "lookup failed")
    except Exception as exc:
        logger.warning(f"[ip] Geolocation lookup failed for {ip_address}: {exc}")
        result["geolocation_error"] = str(exc)

    logger.info(f"[ip] Resolved {domain} -> {ip_address}")
    return result
