"""
Basic security observations module.

Deliberately takes the already-fetched HTTP headers as input rather
than making its own request — this module's one responsibility is
interpreting data, not collecting it. Keeping collection and
analysis separate means either one can change without touching the
other.

This is a lightweight, non-intrusive checklist, not a substitute for
a full header/config audit — it flags common, well-known gaps so a
reader knows where to look first.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger("reconkit")

# header_name -> (human label, why it matters)
SECURITY_HEADERS = {
    "content-security-policy": (
        "Content-Security-Policy",
        "Restricts which sources scripts, styles, and other resources can load from, "
        "reducing the impact of injected content.",
    ),
    "strict-transport-security": (
        "HTTP Strict-Transport-Security (HSTS)",
        "Tells browsers to only ever connect over HTTPS, preventing protocol-downgrade "
        "and some man-in-the-middle attacks.",
    ),
    "x-frame-options": (
        "X-Frame-Options",
        "Prevents the page from being embedded in a frame on another site, mitigating "
        "clickjacking.",
    ),
    "x-content-type-options": (
        "X-Content-Type-Options",
        "Stops browsers from guessing content types, reducing certain script-injection "
        "vectors.",
    ),
    "referrer-policy": (
        "Referrer-Policy",
        "Controls how much URL information is leaked to other sites via the Referer header.",
    ),
    "permissions-policy": (
        "Permissions-Policy",
        "Restricts which browser features (camera, geolocation, etc.) the page may use.",
    ),
}

BANNER_HEADERS = ["server", "x-powered-by", "x-aspnet-version", "x-generator"]


def run(headers_result: Dict[str, Any]) -> Dict[str, Any]:
    if not headers_result or "headers" not in headers_result:
        logger.warning("[security_observations] No HTTP headers available to analyze")
        return {"error": "No HTTP headers were collected for this target"}

    raw_headers = {k.lower(): v for k, v in headers_result["headers"].items()}

    missing: List[Dict[str, str]] = []
    present: List[str] = []
    for key, (label, reason) in SECURITY_HEADERS.items():
        if key in raw_headers:
            present.append(label)
        else:
            missing.append({"header": label, "risk": reason})

    banner_exposure = {}
    for key in BANNER_HEADERS:
        if key in raw_headers:
            banner_exposure[key] = raw_headers[key]

    logger.info(
        f"[security_observations] {len(present)} security headers present, "
        f"{len(missing)} missing, {len(banner_exposure)} banner header(s) exposed"
    )

    return {
        "headers_present": present,
        "headers_missing": missing,
        "banner_exposure": banner_exposure,
    }
