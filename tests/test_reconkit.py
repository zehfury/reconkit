"""
Lightweight unit tests.

These deliberately avoid hitting the network — they test the parts
of the framework that don't depend on an external target being
reachable: input normalization, and that every collection module
degrades to a predictable {"error": ...} shape instead of raising
when given garbage input.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import normalize_domain
from reconkit import dns_records, ip_geolocation, ssl_info, whois_lookup


def test_normalize_domain_strips_scheme():
    assert normalize_domain("https://example.com") == "example.com"
    assert normalize_domain("http://example.com") == "example.com"


def test_normalize_domain_strips_path():
    assert normalize_domain("example.com/some/path") == "example.com"
    assert normalize_domain("https://example.com/some/path?q=1") == "example.com"


def test_normalize_domain_bare_domain_unchanged():
    assert normalize_domain("example.com") == "example.com"


def test_whois_invalid_domain_returns_error_not_exception():
    result = whois_lookup.run("this-domain-should-not-exist-xyz123.invalid")
    assert isinstance(result, dict)
    assert "error" in result or result.get("registrar") is None


def test_dns_invalid_domain_returns_empty_lists_not_exception():
    result = dns_records.run("this-domain-should-not-exist-xyz123.invalid")
    assert isinstance(result, dict)
    for record_type in dns_records.RECORD_TYPES:
        assert result[record_type] == []


def test_ssl_invalid_domain_returns_error_not_exception():
    result = ssl_info.run("this-domain-should-not-exist-xyz123.invalid")
    assert isinstance(result, dict)
    assert "error" in result


def test_ip_geolocation_invalid_domain_returns_error_not_exception():
    result = ip_geolocation.run("this-domain-should-not-exist-xyz123.invalid")
    assert isinstance(result, dict)
    assert "error" in result


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL: {test.__name__} — {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    sys.exit(1 if failures else 0)
