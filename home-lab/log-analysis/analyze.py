#!/usr/bin/env python3
"""
Log Analysis Automation Script — SSH Brute Force Detection

Parses system authentication logs (auth.log) to detect SSH brute force
attempts by grouping failed login attempts by source IP and flagging IPs
that exceed configurable thresholds.

Author: Hassan Abdulahi Hassan
Portfolio: https://github.com/hassanwardhere/hassan-security-lab
"""

import argparse
import gzip
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


# ── Regex patterns for auth.log entries ──────────────────────────────

# Generic prefix: matches everything up to "sshd[PID]:" regardless of
# timestamp format (ISO 8601 or classic syslog). Group 1 = "<timestamp> <host>"
# Group 2 = PID. Then the event-specific groups.
PREFIX = r"^(.*?)\s+sshd\[(\d+)\]:\s+"

# Failed password for valid user: ...Failed password for jupiter from 10.0.0.1 port ...
RE_FAILED_VALID = re.compile(
    PREFIX + r"Failed password for (\S+) from (\S+) port \d+"
)

# Failed password for invalid user: ...Failed password for invalid user root from 10.0.0.1 port ...
RE_FAILED_INVALID = re.compile(
    PREFIX + r"Failed password for invalid user (\S+) from (\S+) port \d+"
)

# Successful login: ...Accepted password/publickey for jupiter from 10.0.0.1 port ...
RE_ACCEPTED = re.compile(
    PREFIX + r"Accepted (\S+) for (\S+) from (\S+) port \d+"
)

# Disconnect: ...Disconnected from [authenticating] user jupiter 10.0.0.1 port ...
RE_DISCONNECT = re.compile(
    PREFIX + r"Disconnected from (?:authenticating )?user (\S+) (\S+) port \d+"
)


# ── Time parsing ─────────────────────────────────────────────────────

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def parse_timestamp(prefix: str) -> datetime | None:
    """Parse a timestamp from the log line prefix.

    Handles two formats:
      ISO 8601: "2026-05-31T01:06:15.741844+03:00 hostname"
      Syslog:   "May 31 01:06:18 hostname"
    """
    try:
        # Split into hostname is at the end, timestamp is everything before.
        # The prefix is "<timestamp> <hostname>". We need the first part.
        parts = prefix.strip().split()
        if not parts:
            return None

        # Try ISO 8601 format (first part has T and timezone offset)
        # Handle both "2026-05-31T01:06:18.950587+03:00" and
        # "2026-05-31T01:06:18+03:00"
        ts_str = parts[0]
        if "T" in ts_str and ("+" in ts_str or ("-" in ts_str and ts_str.count("-") >= 3)):
            # Python 3.11+ handles full ISO 8601 natively
            dt = datetime.fromisoformat(ts_str)
            return dt

        # Try syslog format: "May 31 01:06:18"
        if len(parts) >= 3:
            mon = MONTHS.get(parts[0])
            if mon is not None:
                day = int(parts[1])
                time_parts = parts[2].split(":")
                hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
                now = datetime.now(timezone.utc)
                year = now.year
                if mon > now.month:
                    year -= 1
                return datetime(year, mon, day, hour, minute, second, tzinfo=timezone.utc)

        return None
    except (ValueError, IndexError):
        return None


# For pyright — timedelta is used in parse_timestamp
from datetime import timedelta  # noqa: F811


# ── Log file reader ──────────────────────────────────────────────────

def open_log(path: str | Path) -> list[str]:
    """Open a log file, handling .gz compressed archives."""
    path = str(path)
    if path.endswith(".gz"):
        with gzip.open(path, "rt", errors="replace") as f:
            return f.readlines()
    with open(path, "r", errors="replace") as f:
        return f.readlines()


def find_log_files(log_dir: str = "/var/log") -> list[Path]:
    """Find auth.log files in order: auth.log, auth.log.1, auth.log.N.gz."""
    dir_path = Path(log_dir)
    candidates = []
    primary = dir_path / "auth.log"
    if primary.exists():
        candidates.append(primary)
    for i in range(1, 10):
        rotated = dir_path / f"auth.log.{i}"
        if rotated.exists():
            candidates.append(rotated)
        gz = dir_path / f"auth.log.{i}.gz"
        if gz.exists():
            candidates.append(gz)
    return candidates


# ── Log analysis ─────────────────────────────────────────────────────

class LogEntry:
    """A parsed authentication event."""

    def __init__(self, timestamp: datetime, pid: str, event_type: str,
                 username: str, source_ip: str, detail: str = ""):
        self.timestamp = timestamp
        self.pid = pid
        self.event_type = event_type
        self.username = username
        self.source_ip = source_ip
        self.detail = detail


def analyze_logs(log_paths: list[Path]) -> list[LogEntry]:
    """Parse auth log files and return structured LogEntry objects."""
    entries: list[LogEntry] = []

    for path in log_paths:
        try:
            lines = open_log(path)
        except (OSError, PermissionError) as e:
            print(f"  [!] Skipping {path}: {e}", file=sys.stderr)
            continue

        for line in lines:
            line = line.strip()
            if not line:
                continue

            m = RE_FAILED_VALID.match(line)
            if m:
                ts = parse_timestamp(m.group(1))
                if ts:
                    entries.append(LogEntry(ts, m.group(2), "failed",
                                            m.group(3), m.group(4)))
                continue

            m = RE_FAILED_INVALID.match(line)
            if m:
                ts = parse_timestamp(m.group(1))
                if ts:
                    entries.append(LogEntry(ts, m.group(2), "failed_invalid",
                                            m.group(3), m.group(4)))
                continue

            m = RE_ACCEPTED.match(line)
            if m:
                ts = parse_timestamp(m.group(1))
                if ts:
                    entries.append(LogEntry(ts, m.group(2), "accepted",
                                            m.group(4), m.group(5),
                                            detail=f"method={m.group(3)}"))
                continue

            m = RE_DISCONNECT.match(line)
            if m:
                ts = parse_timestamp(m.group(1))
                if ts:
                    entries.append(LogEntry(ts, m.group(2), "disconnect",
                                            m.group(3), m.group(4)))
                continue

    return entries


def detect_brute_force(entries: list[LogEntry],
                       threshold: int = 5,
                       window_minutes: int = 10) -> dict:
    """Group failed attempts by IP and flag those exceeding the threshold."""
    failed = [e for e in entries if e.event_type in ("failed", "failed_invalid")]
    if not failed:
        return {}

    by_ip: dict[str, dict] = {}
    for e in failed:
        if e.source_ip not in by_ip:
            by_ip[e.source_ip] = {
                "attempts": 0,
                "usernames": set(),
                "first_seen": e.timestamp,
                "last_seen": e.timestamp,
            }
        info = by_ip[e.source_ip]
        info["attempts"] += 1
        info["usernames"].add(e.username)
        if e.timestamp < info["first_seen"]:
            info["first_seen"] = e.timestamp
        if e.timestamp > info["last_seen"]:
            info["last_seen"] = e.timestamp

    result = {}
    for ip, info in by_ip.items():
        span = (info["last_seen"] - info["first_seen"]).total_seconds() / 60.0
        rate = info["attempts"] / span if span > 0 else info["attempts"]

        flagged = info["attempts"] >= threshold
        if span > window_minutes and rate >= (threshold / window_minutes):
            flagged = True

        result[ip] = {
            "attempts": info["attempts"],
            "usernames": sorted(info["usernames"]),
            "first_seen": info["first_seen"],
            "last_seen": info["last_seen"],
            "span_minutes": round(span, 1),
            "rate_per_min": round(rate, 2),
            "flagged": flagged,
        }

    return result


def summarize(entries: list[LogEntry], brute_force: dict) -> str:
    """Generate a markdown summary report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    lines.append("# Authentication Log Analysis Report")
    lines.append(f"Generated: {now}")
    lines.append("")

    total = len(entries)
    failed = len([e for e in entries if e.event_type in ("failed", "failed_invalid")])
    accepted = len([e for e in entries if e.event_type == "accepted"])
    flagged_ips = sum(1 for v in brute_force.values() if v["flagged"])
    unique_failed_ips = len(set(e.source_ip for e in entries
                                if e.event_type in ("failed", "failed_invalid")))

    lines.append("## Summary")
    lines.append("")
    lines.append(f"Log entries parsed: {total}")
    lines.append(f"Failed login attempts: {failed}")
    lines.append(f"Successful logins: {accepted}")
    lines.append(f"Unique source IPs (failed): {unique_failed_ips}")
    lines.append(f"Brute-force IPs flagged: {flagged_ips}")
    lines.append("")

    flagged = {k: v for k, v in brute_force.items() if v["flagged"]}
    if flagged:
        lines.append("## Flagged IPs — Brute Force Detected")
        lines.append("")
        for ip, info in sorted(flagged.items(), key=lambda x: -x[1]["attempts"]):
            lines.append(f"### {ip}")
            lines.append(f"- **Failed attempts:** {info['attempts']}")
            lines.append(f"- **Usernames targeted:** {', '.join(info['usernames'])}")
            lines.append(f"- **First attempt:** {info['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **Last attempt:** {info['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **Span:** {info['span_minutes']} minutes")
            lines.append(f"- **Rate:** {info['rate_per_min']} attempts/min")
            lines.append("")
    elif brute_force:
        lines.append("## Brute Force Check")
        lines.append("")
        lines.append("No IPs exceeded the detection threshold.")
        lines.append("")

    clean = {k: v for k, v in brute_force.items() if not v["flagged"]}
    if clean:
        lines.append("## Other Sources (Below Threshold)")
        lines.append("")
        for ip, info in sorted(clean.items(), key=lambda x: -x[1]["attempts"]):
            lines.append(f"- **{ip}:** {info['attempts']} attempts ({', '.join(info['usernames'])}) over {info['span_minutes']} min")
        lines.append("")

    logins = [e for e in entries if e.event_type == "accepted"]
    if logins:
        lines.append("## Successful Logins")
        lines.append("")
        for e in sorted(logins, key=lambda x: x.timestamp, reverse=True)[:50]:
            method = e.detail.replace("method=", "") if e.detail else "password"
            lines.append(f"- {e.timestamp.strftime('%Y-%m-%d %H:%M:%S')} — {e.username} from {e.source_ip} ({method})")
        lines.append("")

    username_counts: dict[str, int] = defaultdict(int)
    for e in entries:
        if e.event_type in ("failed", "failed_invalid"):
            username_counts[e.username] += 1
    if username_counts:
        lines.append("## Most Targeted Usernames")
        lines.append("")
        for user, count in sorted(username_counts.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"- {user}: {count} failed attempts")
        lines.append("")

    lines.append("## Recent Events (Last 20)")
    lines.append("")
    for e in sorted(entries, key=lambda x: x.timestamp, reverse=True)[:20]:
        label = {"failed": "FAILED", "failed_invalid": "FAILED(invalid)",
                 "accepted": "LOGIN", "disconnect": "DISCONN"}.get(e.event_type, e.event_type)
        lines.append(f"- {e.timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{label}] {e.username} from {e.source_ip}")
    lines.append("")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Analyze authentication logs for SSH brute force attempts."
    )
    parser.add_argument(
        "--log-dir", default="/var/log",
        help="Directory containing auth.log files (default: /var/log)",
    )
    parser.add_argument(
        "--threshold", type=int, default=5,
        help="Failed attempts threshold for brute-force flagging (default: 5)",
    )
    parser.add_argument(
        "--window", type=int, default=10,
        help="Time window in minutes for rate calculation (default: 10)",
    )
    parser.add_argument(
        "--report", default=None,
        help="Path to write markdown report (default: stdout only)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress console output, only generate report file",
    )
    args = parser.parse_args()

    log_files = find_log_files(args.log_dir)
    if not log_files:
        print("No auth.log files found.", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"[*] Found {len(log_files)} auth log(s)")
        for p in log_files:
            size = os.path.getsize(p) if os.path.exists(p) else 0
            print(f"    {p.name} ({size / 1024:.1f} KB)")

    entries = analyze_logs(log_files)
    if not entries:
        print("[*] No SSH authentication events found in logs.")
        sys.exit(0)

    if not args.quiet:
        failed = len([e for e in entries if e.event_type in ("failed", "failed_invalid")])
        accepted = len([e for e in entries if e.event_type == "accepted"])
        print(f"\n[*] Parsed {len(entries)} events: {failed} failed, {accepted} successful")

    brute_force = detect_brute_force(entries, args.threshold, args.window)
    flagged = {k: v for k, v in brute_force.items() if v["flagged"]}

    if not args.quiet:
        if flagged:
            print(f"\n[!] BRUTE FORCE DETECTED — {len(flagged)} IP(s) flagged:")
            header = f"{'Source IP':<20} {'Attempts':<10} {'Usernames':<25} {'Span(min)':<10} {'Rate/min':<10}"
            print(header)
            print("-" * len(header))
            for ip, info in sorted(flagged.items(), key=lambda x: -x[1]["attempts"]):
                users = ", ".join(info["usernames"][:3])
                if len(info["usernames"]) > 3:
                    users += f" (+{len(info['usernames']) - 3})"
                print(f"{ip:<20} {info['attempts']:<10} {users:<25} {info['span_minutes']:<10} {info['rate_per_min']:<10}")
        elif brute_force:
            print(f"\n[*] No IPs exceeded threshold ({args.threshold} failures/{args.window}min)")
        else:
            print("\n[*] No failed login attempts found.")

    report = summarize(entries, brute_force)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        if not args.quiet:
            print(f"\n[*] Report saved to {report_path}")

    if not args.quiet and not flagged:
        print(f"\n[*] Clean bill of health — no brute force detected.")
        logins = [e for e in entries if e.event_type == "accepted"]
        if logins:
            last = max(logins, key=lambda x: x.timestamp)
            print(f"    Last login: {last.username} from {last.source_ip} "
                  f"at {last.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
