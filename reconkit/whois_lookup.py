"""
WHOIS module — registrar, creation/expiry dates, name servers.

Uses python-whois, which shells out to the system `whois` client
where available and falls back to raw socket queries against the
relevant WHOIS server otherwise. Registrars format WHOIS output
inconsistently, so every field is treated as optional.
"""

import logging
from typing import Any, Dict

import whois as whois_lib

logger = logging.getLogger("reconkit")


def _first(value: Any) -> Any:
    """WHOIS libraries often return a list for fields that are
    usually singular (e.g. creation_date). Normalize to one value."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def run(domain: str) -> Dict[str, Any]:
    logger.info(f"[whois] Querying WHOIS for {domain}")
    try:
        record = whois_lib.whois(domain)

        if not record or not record.get("domain_name"):
            logger.warning(f"[whois] No WHOIS record returned for {domain}")
            return {"error": "No WHOIS record found (privacy-protected or unsupported TLD)"}

        result = {
            "registrar": _first(record.get("registrar")),
            "creation_date": str(_first(record.get("creation_date"))),
            "expiration_date": str(_first(record.get("expiration_date"))),
            "updated_date": str(_first(record.get("updated_date"))),
            "name_servers": record.get("name_servers"),
            "status": record.get("status"),
            "org": record.get("org"),
            "country": record.get("country"),
        }
        logger.info(f"[whois] Retrieved registrar: {result.get('registrar')}")
        return result

    except Exception as exc:
        logger.error(f"[whois] Failed for {domain}: {exc}")
        return {"error": str(exc)}
