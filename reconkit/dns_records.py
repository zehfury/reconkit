"""
DNS module — A, AAAA, MX, NS, TXT, CNAME records.

Each record type is queried independently. A domain missing one
record type (e.g. no AAAA) is normal, not a failure — only query
errors (timeout, NXDOMAIN, no nameservers reachable) are logged as
warnings and produce an empty list for that type.
"""

import logging
from typing import Any, Dict, List

import dns.resolver

logger = logging.getLogger("reconkit")

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]


def _query(domain: str, record_type: str) -> List[str]:
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = resolver.resolve(domain, record_type)
        return [str(rdata).strip() for rdata in answers]
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        logger.warning(f"[dns] {domain} does not exist (NXDOMAIN)")
        return []
    except Exception as exc:
        logger.warning(f"[dns] {record_type} lookup failed for {domain}: {exc}")
        return []


def run(domain: str) -> Dict[str, Any]:
    logger.info(f"[dns] Resolving DNS records for {domain}")
    result: Dict[str, Any] = {}
    for record_type in RECORD_TYPES:
        result[record_type] = _query(domain, record_type)

    found = [t for t in RECORD_TYPES if result[t]]
    logger.info(f"[dns] Found record types: {found or 'none'}")
    return result
