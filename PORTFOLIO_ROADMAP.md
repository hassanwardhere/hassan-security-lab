# Hassan Security Lab — Portfolio Roadmap

> **Managed by Hermes (Jupiter)**. Update status after each completed task.
> Last updated: 2026-06-05

---

## Phase 1 — SOC / Blue Team Core Stack

| # | Project | Status | Commit | Notes |
|---|---------|--------|--------|-------|
| 1 | Wazuh SIEM | ✅ Done | — | Upgraded to 4.14.5, custom rules, dashboards |
| 2 | ELK Stack | ✅ Done | — | Integrated with Wazuh, logs flowing |
| 3 | Snort IDS | ✅ Done | — | 46 custom detection rules |
| 4 | Velociraptor EDR | ✅ Done | 1374d81 | Documented, Docker compose config |
| 5 | Shuffle SOAR | ✅ Done | — | Documented, Wazuh + MISP integration |
| 6 | MISP Threat Intel | ✅ Done | 8543f34 | Fully deployed, docker-compose fixed, Wazuh CDB integration documented |

---

## Phase 2 — Scripting & Automation

| # | Project | Status | Commit | Notes |
|---|---------|--------|--------|-------|
| 7 | Python Vulnerability Scanner | ✅ Done | ac7d1b3 | TCP scan, service detection, NVD CVE lookup, markdown reports |
| 8 | Log Analysis Automation | ✅ Done | c88f542 | Parses auth logs, SSH brute force detection, markdown reports |
| 9 | File Integrity Monitor | ⏳ Pending | — | Detects file changes, Telegram alerts |

---

## Phase 3 — Infrastructure & Cloud Security

| # | Project | Status | Commit | Notes |
|---|---------|--------|--------|-------|
| 10 | Docker Security Hardening | ⏳ Pending | — | CIS benchmark, documented |
| 11 | Cloudflare Security Write-up | ⏳ Pending | — | WAF, zero trust, tunnel config |
| 12 | Linux Server Hardening Script | ⏳ Pending | — | Automated CIS benchmark checks |

---

## Phase 4 — Threat Analysis

| # | Project | Status | Commit | Notes |
|---|---------|--------|--------|-------|
| 13 | Phishing Email Analyzer | ⏳ Pending | — | Header parsing, IOC checks against MISP |
| 14 | Threat Hunt Report | ⏳ Pending | — | Documented hunt using MISP + Wazuh |

---

## Schedule

| Date | Task |
|------|------|
| 2026-05-30 (Sat) | MISP — complete live deployment docs — ✅ Done |
| 2026-06-03 (Wed) | Python Vulnerability Scanner — ✅ Done |
| 2026-06-04 (Thu) | Log Analysis Automation Script — ✅ Done |
| 2026-06-06 (Sat) | File Integrity Monitor |
| 2026-06-09 (Tue) | Docker Security Hardening |
| 2026-06-11 (Thu) | Cloudflare Security Write-up |
| 2026-06-13 (Sat) | Linux Server Hardening Script |
| 2026-06-16 (Tue) | Phishing Email Analyzer |
| 2026-06-18 (Thu) | Threat Hunt Report |

---

## Hermes Instructions

When completing a project:
1. Update the Status column to ✅ Done
2. Add the commit hash to the Commit column
3. Add any relevant notes
4. Push this file to GitHub with message: `Update PORTFOLIO_ROADMAP.md — [Project Name] complete`
5. Send Telegram confirmation with commit URL

Next pending task: Check this file first before starting any portfolio work.
