"""
Report generator module.

Takes the full results dict produced by main.py and renders it into
a single, structured Markdown report — the kind handed to a client
before an engagement starts. This module only formats; it never
collects or interprets data itself, so report layout can change
without touching any collection module.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("reconkit")


def _bool_icon(value: bool) -> str:
    return "Yes" if value else "No"


def _section_whois(data: Dict[str, Any]) -> str:
    if "error" in data:
        return f"_Could not retrieve WHOIS data: {data['error']}_\n"
    lines = [
        f"- **Registrar:** {data.get('registrar') or 'Not disclosed'}",
        f"- **Organization:** {data.get('org') or 'Not disclosed'}",
        f"- **Country:** {data.get('country') or 'Not disclosed'}",
        f"- **Creation Date:** {data.get('creation_date') or 'Unknown'}",
        f"- **Expiration Date:** {data.get('expiration_date') or 'Unknown'}",
        f"- **Last Updated:** {data.get('updated_date') or 'Unknown'}",
        f"- **Name Servers:** {', '.join(data.get('name_servers') or []) or 'None found'}",
    ]
    return "\n".join(lines) + "\n"


def _section_dns(data: Dict[str, Any]) -> str:
    lines = []
    for record_type, values in data.items():
        if values:
            lines.append(f"- **{record_type}:**")
            for v in values:
                lines.append(f"  - `{v}`")
        else:
            lines.append(f"- **{record_type}:** none found")
    return "\n".join(lines) + "\n"


def _section_ip(data: Dict[str, Any]) -> str:
    if "error" in data:
        return f"_Could not resolve IP address: {data['error']}_\n"
    lines = [f"- **IP Address:** {data.get('ip_address')}"]
    if "geolocation_error" in data:
        lines.append(f"- **Geolocation:** unavailable ({data['geolocation_error']})")
    else:
        lines.extend([
            f"- **Country:** {data.get('country', 'Unknown')}",
            f"- **Region:** {data.get('region', 'Unknown')}",
            f"- **City:** {data.get('city', 'Unknown')}",
            f"- **ISP / Org:** {data.get('isp', 'Unknown')} / {data.get('org', 'Unknown')}",
            f"- **ASN:** {data.get('as', 'Unknown')}",
        ])
    return "\n".join(lines) + "\n"


def _section_http(data: Dict[str, Any]) -> str:
    if "error" in data:
        return f"_Could not retrieve HTTP headers: {data['error']}_\n"
    lines = [
        f"- **Final URL:** {data.get('final_url')}",
        f"- **Status Code:** {data.get('status_code')}",
        f"- **Scheme Used:** {data.get('scheme_used', '').upper()}",
        "",
        "**Raw Response Headers:**",
        "```",
    ]
    for k, v in data.get("headers", {}).items():
        lines.append(f"{k}: {v}")
    lines.append("```")
    return "\n".join(lines) + "\n"


def _section_ssl(data: Dict[str, Any]) -> str:
    if "error" in data:
        return f"_Could not retrieve certificate: {data['error']}_\n"
    lines = [
        f"- **Issuer:** {data.get('issuer') or 'Unknown'}",
        f"- **Subject (CN):** {data.get('subject') or 'Unknown'}",
        f"- **Valid From:** {data.get('valid_from')}",
        f"- **Valid Until:** {data.get('valid_until')}",
        f"- **Days Until Expiry:** {data.get('days_until_expiry', 'Unknown')}",
        f"- **Subject Alternative Names:** {', '.join(data.get('san') or []) or 'None'}",
    ]
    return "\n".join(lines) + "\n"


def _section_robots_sitemap(data: Dict[str, Any]) -> str:
    parts = []
    for key, label in [("robots_txt", "robots.txt"), ("sitemap_xml", "sitemap.xml")]:
        entry = data.get(key, {})
        parts.append(f"**{label}:**\n")
        if entry.get("found"):
            content = entry.get("content", "").strip()
            note = " _(truncated)_" if entry.get("truncated") else ""
            parts.append(f"Found (HTTP {entry.get('status_code')}){note}\n")
            parts.append("```\n" + (content or "(empty file)") + "\n```\n")
        elif "error" in entry:
            parts.append(f"Could not retrieve: {entry['error']}\n")
        else:
            parts.append(f"Not found (HTTP {entry.get('status_code', 'N/A')})\n")
    return "\n".join(parts)


def _section_security(data: Dict[str, Any]) -> str:
    if "error" in data:
        return f"_{data['error']}_\n"
    lines = ["**Security Headers Present:**"]
    lines.append(", ".join(data.get("headers_present") or []) or "None")
    lines.append("")
    lines.append("**Missing Security Headers:**")
    missing = data.get("headers_missing") or []
    if not missing:
        lines.append("None — all checked headers are present.")
    else:
        for item in missing:
            lines.append(f"- **{item['header']}** — {item['risk']}")
    lines.append("")
    banner = data.get("banner_exposure") or {}
    lines.append("**Server / Technology Banner Exposure:**")
    if banner:
        for k, v in banner.items():
            lines.append(f"- `{k}`: {v}")
    else:
        lines.append("None observed.")
    return "\n".join(lines) + "\n"


def generate(target: str, results: Dict[str, Any], output_dir: str = "reports") -> str:
    logger.info(f"[report] Generating report for {target}")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    filename_ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    safe_target = target.replace(":", "_").replace("/", "_")
    output_path = Path(output_dir) / f"recon-report-{safe_target}-{filename_ts}.md"

    report = f"""# Reconnaissance Report

**Target:** `{target}`
**Generated:** {timestamp}
**Tool:** reconkit v0.1

---

## 1. Executive Summary

This report presents the results of an automated, passive reconnaissance
scan against `{target}`. All data was collected from publicly available
sources (WHOIS, DNS, HTTP, and TLS) with no intrusive testing, exploitation,
or authentication bypass attempted. Findings below should be reviewed
before any further, authorized engagement steps are taken.

## 2. WHOIS Information

{_section_whois(results.get("whois", {}))}

## 3. DNS Records

{_section_dns(results.get("dns", {}))}

## 4. IP Address & Geolocation

{_section_ip(results.get("ip", {}))}

_Note: geolocation is based on the resolved IP and is often approximate —
it may reflect a CDN, hosting provider, or cloud region rather than the
organization's physical location._

## 5. HTTP Response Headers

{_section_http(results.get("http", {}))}

## 6. SSL/TLS Certificate

{_section_ssl(results.get("ssl", {}))}

## 7. robots.txt & sitemap.xml

{_section_robots_sitemap(results.get("robots_sitemap", {}))}

## 8. Basic Security Observations

{_section_security(results.get("security", {}))}

---

## Disclaimer

This report was generated using only passive, publicly available
information. No authentication was bypassed, no exploitation was
attempted, and no intrusive scanning was performed against the target.
This tool is intended for use only against domains you own or are
explicitly authorized to assess.
"""

    output_path.write_text(report, encoding="utf-8")
    logger.info(f"[report] Report written to {output_path}")
    return str(output_path)
