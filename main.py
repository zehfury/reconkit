#!/usr/bin/env python3
"""
reconkit — Web Recon Automation Framework

Usage:
    python main.py <domain>
    python main.py           # will prompt for a domain interactively

Example:
    python main.py example.com
"""

import argparse
import sys
import time

from reconkit import dns_records, http_headers, ip_geolocation
from reconkit import robots_sitemap, security_observations, ssl_info, whois_lookup
from reconkit.logger import get_logger
from reconkit.report_generator import generate

logger = get_logger()

# Each entry: (result_key, human label, callable)
# Kept as an ordered list (not a dict of lambdas scattered through the
# file) so adding/removing/reordering a module is a one-line change here,
# and nowhere else.
MODULES = [
    ("whois", "WHOIS", lambda d: whois_lookup.run(d)),
    ("dns", "DNS Records", lambda d: dns_records.run(d)),
    ("ip", "IP & Geolocation", lambda d: ip_geolocation.run(d)),
    ("http", "HTTP Headers", lambda d: http_headers.run(d)),
    ("ssl", "SSL/TLS Certificate", lambda d: ssl_info.run(d)),
    ("robots_sitemap", "robots.txt / sitemap.xml", lambda d: robots_sitemap.run(d)),
]


def normalize_domain(raw: str) -> str:
    """Accept a bare domain or a full URL and return just the hostname."""
    raw = raw.strip()
    for prefix in ("https://", "http://"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    return raw.split("/")[0].strip()


def run_all(domain: str) -> dict:
    results = {}
    for key, label, func in MODULES:
        start = time.time()
        try:
            results[key] = func(domain)
        except Exception as exc:
            # Belt-and-suspenders: modules already catch their own
            # errors, but the orchestrator never trusts that blindly —
            # one module's bug should never end the whole run.
            logger.error(f"[main] Unexpected failure in module '{label}': {exc}")
            results[key] = {"error": f"Unhandled module failure: {exc}"}
        elapsed = time.time() - start
        logger.info(f"[main] {label} finished in {elapsed:.2f}s")

    # security_observations analyzes the http module's output rather
    # than fetching anything itself, so it runs after http_headers
    # and is fed that result directly.
    try:
        results["security"] = security_observations.run(results.get("http", {}))
    except Exception as exc:
        logger.error(f"[main] Unexpected failure in module 'Security Observations': {exc}")
        results["security"] = {"error": f"Unhandled module failure: {exc}"}

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="reconkit — passive web reconnaissance automation framework"
    )
    parser.add_argument(
        "domain", nargs="?", help="Target domain or URL (e.g. example.com)"
    )
    parser.add_argument(
        "-o", "--output-dir", default="reports", help="Directory to write the report to"
    )
    args = parser.parse_args()

    raw_target = args.domain or input("Enter target domain or URL: ")
    domain = normalize_domain(raw_target)

    if not domain:
        logger.error("[main] No domain provided. Exiting.")
        sys.exit(1)

    logger.info(f"[main] Starting reconnaissance run against {domain}")
    start_time = time.time()

    results = run_all(domain)
    report_path = generate(domain, results, output_dir=args.output_dir)

    total_time = time.time() - start_time
    logger.info(f"[main] Run complete in {total_time:.2f}s. Report: {report_path}")

    print(f"\nReconnaissance complete.\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
