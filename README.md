# reconkit — Web Recon Automation Framework

A modular, passive web reconnaissance tool. Give it a domain, it collects
publicly available information about that target across WHOIS, DNS, HTTP,
and TLS, and compiles it into a single Markdown report you could hand to a
client before a penetration test begins.

Built as part of a cybersecurity internship at Cryptonic. The goal was to
engineer the tool, not to run someone else's scanner with my name on it.

## What It Collects

- WHOIS information (registrar, creation/expiry dates, name servers)
- DNS records (A, AAAA, MX, NS, TXT, CNAME)
- IP address and coarse geolocation
- HTTP response headers
- SSL/TLS certificate details (issuer, validity, expiry)
- robots.txt and sitemap.xml content
- Basic security observations (missing CSP/HSTS/X-Frame-Options, exposed server banners)

All of this is passive. Nothing in this tool authenticates, brute-forces,
fuzzes, or sends any payload to the target. It only reads what the target
already publishes.

## Installation

```bash
git clone <this-repo-url>
cd reconkit
pip install -r requirements.txt
```

Requires Python 3.9+. On some Linux distributions, `python-whois` works
better if the system `whois` client is also installed:

```bash
sudo apt install whois
```

## Usage

```bash
python main.py example.com
```

Or run it without an argument and it will prompt you:

```bash
python main.py
Enter target domain or URL: example.com
```

Both bare domains (`example.com`) and full URLs (`https://example.com/path`)
are accepted — the tool strips the scheme and path down to the hostname.

Reports are written to `reports/` by default. Use `-o` to change that:

```bash
python main.py example.com -o my-reports
```

A full run log is also written to `logs/reconkit.log`, in addition to the
summary printed to the console.

## Project Structure

```
reconkit/
├── main.py                        # Entry point — orchestrates all modules
├── reconkit/
│   ├── logger.py                  # Shared logging setup
│   ├── whois_lookup.py            # WHOIS module
│   ├── dns_records.py             # DNS records module
│   ├── ip_geolocation.py          # IP resolution + geolocation module
│   ├── http_headers.py            # HTTP response headers module
│   ├── ssl_info.py                # SSL/TLS certificate module
│   ├── robots_sitemap.py          # robots.txt / sitemap.xml module
│   ├── security_observations.py   # Analyzes headers collected by http_headers
│   └── report_generator.py        # Renders results into a Markdown report
├── tests/
│   └── test_reconkit.py           # Offline unit tests (no network required)
├── reports/                       # Generated reports land here
└── requirements.txt
```

## What Each Module Does

| Module | Responsibility |
|---|---|
| `whois_lookup` | Queries WHOIS for registrar, creation/expiry dates, org, and name servers. |
| `dns_records` | Resolves A, AAAA, MX, NS, TXT, and CNAME records independently. |
| `ip_geolocation` | Resolves the domain to an IP, then queries ip-api.com for coarse geolocation. |
| `http_headers` | Fetches the target over HTTPS (falling back to HTTP), returns status code and raw headers. |
| `ssl_info` | Opens a raw TLS connection on port 443 and reads the certificate directly via the standard library. |
| `robots_sitemap` | Fetches `/robots.txt` and `/sitemap.xml`, treating a 404 as a normal result, not a failure. |
| `security_observations` | Takes the headers already collected by `http_headers` and flags missing security headers and exposed server banners. It does not make its own network request. |
| `report_generator` | Formats the collected results dict into a single Markdown report. Formatting only — it never collects or interprets data. |

## Architecture Note

Every collection module follows the same contract: it takes a domain string
in, and returns a plain dict out. It never raises — any failure (timeout,
NXDOMAIN, connection refused, malformed response) is caught inside the
module and returned as `{"error": "..."}` instead. `main.py` wraps every
module call in its own `try/except` on top of that as a second layer of
protection, so even a bug I didn't anticipate in one module can't take
down the rest of the run.

This is why WHOIS, DNS, IP, HTTP, TLS, and robots/sitemap are six separate
files instead of one script: each one talks to a different protocol or
service, fails in different ways, and needs to be testable and replaceable
on its own. `security_observations` is deliberately its own module even
though it makes no network calls of its own — it consumes the headers
`http_headers` already collected. Splitting collection from analysis means
I can change what counts as a "missing security header" without touching
anything that talks to the network, and vice versa.

`report_generator` is the same idea applied to output: it has no idea how
any piece of data was collected, only how to lay it out. If I swap
Markdown for HTML later, no collection module changes.

## Limitations

- **WHOIS** depends on the registrar's WHOIS server responding, and format
  varies enough between registrars that some fields (org, country) are
  sometimes empty even on a successful query. Some TLDs also restrict WHOIS
  entirely.
- **Geolocation** is IP-based and approximate. A result often reflects a
  CDN or cloud provider's location (e.g. Cloudflare, AWS), not the
  organization's actual address.
- **DNS resolution** depends on the resolver's own network access; on a
  restricted or firewalled network, some record types may time out even
  though the domain is otherwise reachable.
- **Geolocation API** (ip-api.com) is a free, unauthenticated endpoint and
  is rate-limited. Heavy or repeated use against many domains may get
  temporarily throttled.
- This tool performs **no active exploitation or authentication testing**.
  It is a reconnaissance aid, not a vulnerability scanner — it does not
  replace manual verification of anything it reports.

## Sample Report

A sample report generated against an authorized test domain is included in
`reports/`. Every run produces a new timestamped file so past reports are
never overwritten.

## Disclaimer

This tool is intended only for domains you own or are explicitly authorized
to assess. It performs passive reconnaissance using publicly available
information — WHOIS, DNS, HTTP, and TLS — and does not perform any
intrusive testing. Running it against systems without authorization may
violate the law and/or terms of service in your jurisdiction.
