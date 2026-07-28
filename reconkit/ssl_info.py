"""
SSL/TLS certificate module.

Opens a raw TLS connection on port 443 and reads the peer
certificate directly via the standard library ssl module — no
external dependency needed for this one. Handles plain-HTTP-only
targets (no cert to read) and expired/self-signed certs (still
worth reporting, not a crash condition) as separate, expected
outcomes rather than errors.
"""

import logging
import socket
import ssl
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger("reconkit")

CERT_DATE_FORMAT = "%b %d %H:%M:%S %Y %Z"
CONNECT_TIMEOUT = 6


def run(domain: str) -> Dict[str, Any]:
    logger.info(f"[ssl] Retrieving TLS certificate for {domain}")
    context = ssl.create_default_context()

    try:
        with socket.create_connection((domain, 443), timeout=CONNECT_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))
        not_before = cert.get("notBefore")
        not_after = cert.get("notAfter")

        days_remaining = None
        if not_after:
            try:
                expiry = datetime.strptime(not_after, CERT_DATE_FORMAT)
                days_remaining = (expiry - datetime.utcnow()).days
            except ValueError:
                pass

        result = {
            "issuer": issuer.get("organizationName") or issuer.get("commonName"),
            "subject": subject.get("commonName"),
            "valid_from": not_before,
            "valid_until": not_after,
            "days_until_expiry": days_remaining,
            "san": [entry[1] for entry in cert.get("subjectAltName", [])],
        }
        logger.info(f"[ssl] Certificate issued by {result['issuer']}, expires {not_after}")
        return result

    except ssl.SSLCertVerificationError as exc:
        logger.warning(f"[ssl] Certificate verification failed for {domain}: {exc}")
        return {"error": f"Certificate verification failed: {exc}"}
    except (socket.timeout, ConnectionRefusedError, OSError) as exc:
        logger.warning(f"[ssl] Could not connect on port 443 for {domain}: {exc}")
        return {"error": f"No TLS service on port 443: {exc}"}
    except Exception as exc:
        logger.error(f"[ssl] Unexpected error for {domain}: {exc}")
        return {"error": str(exc)}
