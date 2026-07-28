# Reconnaissance Report

**Target:** `example.com`
**Generated:** 2026-07-28 14:49 UTC
**Tool:** reconkit v0.1

---

## 1. Executive Summary

This report presents the results of an automated, passive reconnaissance
scan against `example.com`. All data was collected from publicly available
sources (WHOIS, DNS, HTTP, and TLS) with no intrusive testing, exploitation,
or authentication bypass attempted. Findings below should be reviewed
before any further, authorized engagement steps are taken.

## 2. WHOIS Information

- **Registrar:** RESERVED-Internet Assigned Numbers Authority
- **Organization:** Not disclosed
- **Country:** Not disclosed
- **Creation Date:** 1995-08-14 04:00:00+00:00
- **Expiration Date:** 2026-08-13 04:00:00+00:00
- **Last Updated:** 2026-01-16 18:26:50+00:00
- **Name Servers:** ELLIOTT.NS.CLOUDFLARE.COM, HERA.NS.CLOUDFLARE.COM


## 3. DNS Records

- **A:**
  - `104.20.23.154`
  - `172.66.147.243`
- **AAAA:**
  - `2606:4700:10::6814:179a`
  - `2606:4700:10::ac42:93f3`
- **MX:**
  - `0 .`
- **NS:**
  - `hera.ns.cloudflare.com.`
  - `elliott.ns.cloudflare.com.`
- **TXT:**
  - `"v=spf1 -all"`
  - `"_k2n1y4vw3qtb4skdx9e7dxt97qrmmq9"`
- **CNAME:** none found


## 4. IP Address & Geolocation

- **IP Address:** 104.20.23.154
- **Country:** Canada
- **Region:** Ontario
- **City:** Toronto
- **ISP / Org:** Cloudflare, Inc. / Cloudflare, Inc.
- **ASN:** AS13335 Cloudflare, Inc.


_Note: geolocation is based on the resolved IP and is often approximate —
it may reflect a CDN, hosting provider, or cloud region rather than the
organization's physical location._

## 5. HTTP Response Headers

- **Final URL:** https://example.com/
- **Status Code:** 200
- **Scheme Used:** HTTPS

**Raw Response Headers:**
```
Date: Tue, 28 Jul 2026 14:48:57 GMT
Content-Type: text/html
Transfer-Encoding: chunked
Connection: keep-alive
Server: cloudflare
last-modified: Tue, 21 Jul 2026 07:16:00 GMT
allow: GET, HEAD
Age: 6473
cf-cache-status: HIT
Content-Encoding: br
CF-RAY: a224b011cf47fc46-AMS
```


## 6. SSL/TLS Certificate

- **Issuer:** SSL Corporation
- **Subject (CN):** example.com
- **Valid From:** May 31 21:39:12 2026 GMT
- **Valid Until:** Aug 29 21:41:26 2026 GMT
- **Days Until Expiry:** 32
- **Subject Alternative Names:** example.com, *.example.com


## 7. robots.txt & sitemap.xml

**robots.txt:**

Not found (HTTP 404)

**sitemap.xml:**

Not found (HTTP 404)


## 8. Basic Security Observations

**Security Headers Present:**
None

**Missing Security Headers:**
- **Content-Security-Policy** — Restricts which sources scripts, styles, and other resources can load from, reducing the impact of injected content.
- **HTTP Strict-Transport-Security (HSTS)** — Tells browsers to only ever connect over HTTPS, preventing protocol-downgrade and some man-in-the-middle attacks.
- **X-Frame-Options** — Prevents the page from being embedded in a frame on another site, mitigating clickjacking.
- **X-Content-Type-Options** — Stops browsers from guessing content types, reducing certain script-injection vectors.
- **Referrer-Policy** — Controls how much URL information is leaked to other sites via the Referer header.
- **Permissions-Policy** — Restricts which browser features (camera, geolocation, etc.) the page may use.

**Server / Technology Banner Exposure:**
- `server`: cloudflare


---

## Disclaimer

This report was generated using only passive, publicly available
information. No authentication was bypassed, no exploitation was
attempted, and no intrusive scanning was performed against the target.
This tool is intended for use only against domains you own or are
explicitly authorized to assess.
