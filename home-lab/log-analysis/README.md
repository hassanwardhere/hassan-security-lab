# Log Analysis Automation — SSH Brute Force Detection

Parses system authentication logs (auth.log) to detect SSH brute force attempts. Flags source IPs that exceed a configurable failure threshold within a time window, and generates markdown reports with detailed findings.

## Features

- **Multi-source parsing** — Reads auth.log, auth.log.1, auth.log.N.gz (rotated archives)
- **SSH event detection** — Failed passwords (valid + invalid users), successful logins, disconnects
- **Brute force detection** — Groups attempts by source IP, flags IPs exceeding configurable thresholds
- **Username targeting analysis** — Identifies which usernames are being attacked
- **Rate analysis** — Computes attempts-per-minute for each source IP
- **Markdown reports** — Full report with flagged IPs, successful logins, and targeting stats
- **No root required** — Reads log files as a regular user (log file group permissions permitting)
- **Pure Python** — No external dependencies, stdlib only

## Installation

```bash
# Clone the repo
git clone https://github.com/hassanwardhere/hassan-security-lab.git
cd hassan-security-lab/home-lab/log-analysis

# No dependencies needed — pure stdlib
```

## Usage

```bash
# Default analysis (auth.log in /var/log)
python analyze.py

# Custom log directory
python analyze.py --log-dir /custom/path

# Adjust detection sensitivity
python analyze.py --threshold 10 --window 15

# Save markdown report
python analyze.py --report ./reports/auth-report.md

# Quiet mode — report file only, no console output
python analyze.py --report ./reports/auth-report.md --quiet
```

### Output

Console shows a summary with flagged IPs when brute force is detected:

```
[*] Found 3 auth log(s)
    auth.log (422.9 KB)
    auth.log.1 (1.2 MB)
    auth.log.2.gz (458.3 KB)

[*] Parsed 847 events: 312 failed, 12 successful

[!] BRUTE FORCE DETECTED — 2 IP(s) flagged:
Source IP            Attempts   Usernames            Span(min)   Rate/min
----------------------------------------------------------------------
10.0.0.1             247        root, admin, jupiter  12.3        20.08
203.0.113.42         89         root, ubuntu          8.1         10.99
```

The markdown report (when `--report` is used) includes flagged IPs with full details, successful login history, most-targeted usernames, and recent event timeline.

## How It Works

1. **Log discovery** — Finds auth.log, auth.log.1, and compressed auth.log.N.gz files in order
2. **Regex parsing** — Extracts SSH events (Failed password, Accepted, Disconnected) with timestamps, PIDs, usernames, and source IPs
3. **Time parsing** — Converts syslog timestamps (e.g. `May 31 01:06:18`) to datetime objects, handling year rollover
4. **Grouping** — Groups failed attempts by source IP, calculates span and rate
5. **Flagging** — IPs are flagged if they exceed the failure threshold within the configured time window
6. **Reporting** — Generates structured markdown with flagged IPs, login history, and targeting analysis

## Portfolio Relevance

- **Log analysis** — Real-world syslog parsing and event correlation
- **Threat detection** — Brute force identification methodology
- **Regex engineering** — Robust pattern matching for structured log formats
- **Security automation** — Scripted incident detection without a SIEM
- **Clean code** — Typed Python, modular architecture, comprehensive README

## Limitations

- Only parses SSH authentication events (not sudo, cron, or other PAM events)
- Requires read access to auth.log (typically via `adm` group membership)
- Timestamps lack year information (assumes current year, with rollover handling)
- No real-time monitoring — analyzes static log files on demand

## License

Portfolio project — MIT
