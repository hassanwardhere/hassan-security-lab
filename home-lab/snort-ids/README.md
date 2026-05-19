# Snort IDS - Project 2

**Author:** Hassan Abdulahi Hassan  
**Project:** Home Lab - Intrusion Detection System  
**Date:** May 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Detection Rules](#detection-rules)
5. [Testing](#testing)
6. [ELK Integration](#ell-integration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Overview

This project deploys Snort as a Network-based Intrusion Detection System (NIDS) to monitor network traffic and detect potential security threats. The deployment uses Docker containers for easy management and scalability, with logs formatted for integration with the ELK stack.

### Key Features

- **Real-time Traffic Analysis** - Monitors network traffic in real-time
- **Custom Detection Rules** - Tailored rules for common attacks
- **JSON Alert Output** - Structured logging for SIEM integration
- **Docker-based Deployment** - Easy to deploy and manage
- **Filebeat Integration** - Ready for ELK stack integration

---

## Architecture

### Network Diagram

```
+------------------+         +---------------------+         +------------------+
|   Internet       | <-----> |   Snort IDS Sensor  | <-----> |   ELK Stack      |
|                  |         |   (Docker Container)|         |   (Log Analysis) |
+------------------+         +---------------------+         +------------------+
                                      |
                                      v
                            +---------------------+
                            |   Filebeat          |
                            |   (Log Shipper)     |
                            +---------------------+
```

### Components

| Component | Description | Purpose |
|-----------|-------------|---------|
| Snort IDS | Network intrusion detection system | Monitor and analyze network traffic |
| Filebeat | Log shipper | Forward logs to ELK stack |
| Docker | Containerization platform | Isolate and manage services |
| HDD Storage | `/mnt/hdd/snort/logs` | Persistent log storage |

### Network Mode

The Snort container uses `network_mode: host` to capture all network traffic on the host interface. This provides:
- Full visibility of network traffic
- No NAT overhead
- Direct access to network interfaces

---

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Linux host with root/sudo access
- Available storage at `/mnt/hdd`
- Network interface configured (typically `eth0`)

### Installation Steps

1. **Create log directory on HDD:**
```bash
sudo mkdir -p /mnt/hdd/snort/logs
sudo chmod 755 /mnt/hdd/snort/logs
```

2. **Clone or navigate to the project directory:**
```bash
cd ~/cybersecurity-portfolio/home-lab/snort-ids
```

3. **Start the Snort IDS:**
```bash
docker-compose up -d
```

4. **Verify the container is running:**
```bash
docker-compose ps
docker logs snort-ids
```

5. **Check alert logs:**
```bash
ls -la /mnt/hdd/snort/logs/
```

### Configuration Files

| File | Description | Location |
|------|-------------|----------|
| `snort.conf` | Main Snort configuration | `config/snort.conf` |
| `local.rules` | Custom detection rules | `config/local.rules` |
| `filebeat.yml` | Filebeat configuration | `config/filebeat.yml` |
| `docker-compose.yml` | Docker orchestration | Root directory |

---

## Detection Rules

### Rule Categories

The `local.rules` file includes custom detection rules for the following attack types:

#### 1. SSH Brute Force Detection

| Rule ID | Description | Threshold |
|---------|-------------|-----------|
| 1000001 | Multiple SSH login attempts | 5 attempts / 60 seconds |
| 1000002 | Suspicious SSH connection patterns | 10 connections / 120 seconds |
| 1000003 | SSH authentication failures | 6 failures / 60 seconds |

**Detection Logic:**
- Tracks connection attempts by source IP
- Alerts when thresholds are exceeded
- Identifies common brute force patterns

#### 2. Port Scan Detection

| Rule ID | Description | Scan Type |
|---------|-------------|-----------|
| 1000010 | SYN Scan Detection | SYN flag only |
| 1000011 | FIN Scan Detection | FIN flag only |
| 1000012 | NULL Scan Detection | No flags set |
| 1000013 | XMAS Scan Detection | FIN, URG, PSH flags |
| 1000014 | ACK Scan Detection | ACK flag only |
| 1000015 | UDP Scan Detection | UDP port scanning |
| 1000016 | Vertical Scan | Single host, multiple ports |
| 1000017 | Horizontal Scan | Multiple hosts, single port |

**Scan Types Explained:**

- **SYN Scan:** Sends SYN packets without completing handshake
- **FIN Scan:** Sends packets with FIN flag (bypasses some firewalls)
- **NULL Scan:** Sends packets with no flags set
- **XMAS Scan:** Sets FIN, URG, and PSH flags (lights up like a Christmas tree)
- **ACK Scan:** Used to determine firewall rule sets

#### 3. SQL Injection Detection

| Rule ID | Description | Pattern |
|---------|-------------|---------|
| 1000020 | UNION SELECT detection | `UNION SELECT` |
| 1000021 | Basic SELECT statement | `SELECT...FROM` |
| 1000022 | Comment sequence | `/* */` |
| 1000023 | OR 1=1 bypass | `' OR 1=1` |
| 1000024 | DROP TABLE attempt | `DROP TABLE` |
| 1000025 | xp_cmdshell execution | `xp_cmdshell` |
| 1000026 | Time-based blind SQLi | `SLEEP()` |
| 1000027 | WAITFOR DELAY | `WAITFOR DELAY` |
| 1000028 | File access attempt | `LOAD_FILE` |
| 1000029 | File write attempt | `INTO OUTFILE` |

#### 4. Cross-Site Scripting (XSS) Detection

| Rule ID | Description | Pattern |
|---------|-------------|---------|
| 1000030 | Script tag injection | `<script` |
| 1000031 | JavaScript protocol | `javascript:` |
| 1000032 | onEvent handlers | `onerror=` |
| 1000033 | HTML entity encoding | `&#x;` |
| 1000034 | alert() function | `alert(` |
| 1000035 | Cookie theft | `document.cookie` |
| 1000036 | eval() function | `eval(` |
| 1000037 | document.write injection | `document.write` |

#### 5. Additional Web Attacks

| Rule ID | Description | Attack Type |
|---------|-------------|-------------|
| 1000040 | Directory traversal | `../` |
| 1000041 | URL-encoded traversal | `..%2f` |
| 1000042 | Null byte injection | `%00` |
| 1000043 | Remote file inclusion | `http://` in parameters |
| 1000044 | Local file inclusion | `/etc/passwd` |
| 1000045 | Command injection | `; command` |
| 1000046 | PHP code injection | `<?php` |

---

## Testing

### Testing SSH Brute Force Detection

```bash
# Install hydra for testing
sudo apt install hydra

# Test SSH brute force (against your own test server)
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://target-ip

# Or use nmap for multiple connection attempts
for i in {1..10}; do
    ssh -o ConnectTimeout=2 -o BatchMode=yes test@target-ip 2>/dev/null
done
```

### Testing Port Scan Detection

```bash
# SYN Scan
sudo nmap -sS -p 1-100 target-ip

# FIN Scan
sudo nmap -sF -p 1-100 target-ip

# NULL Scan
sudo nmap -sN -p 1-100 target-ip

# XMAS Scan
sudo nmap -sX -p 1-100 target-ip

# ACK Scan
sudo nmap -sA -p 1-100 target-ip

# UDP Scan
sudo nmap -sU -p 1-100 target-ip
```

### Testing SQL Injection Detection

```bash
# Test with curl
curl "http://target-ip/page.php?id=1' UNION SELECT * FROM users--"
curl "http://target-ip/page.php?id=1' OR 1=1--"
curl "http://target-ip/page.php?id=1; DROP TABLE users--"
```

### Testing XSS Detection

```bash
# Test XSS payloads
curl "http://target-ip/search.php?q=<script>alert(1)</script>"
curl "http://target-ip/search.php?q=<img src=x onerror=alert(1)>"
curl "http://target-ip/search.php?q=javascript:alert(1)"
```

### Verifying Alerts

After running tests, check the logs:

```bash
# View JSON alerts
cat /mnt/hdd/snort/logs/alert.json

# View unified2 logs
ls -la /mnt/hdd/snort/logs/snort.log.*

# Real-time log monitoring
tail -f /mnt/hdd/snort/logs/alert.json
```

---

## ELK Integration

### Filebeat Configuration

Filebeat is configured to:
- Monitor `/var/log/snort/alert.json` for new alerts
- Parse JSON formatted logs
- Forward to Logstash on port 5044

### Logstash Pipeline (Example)

```json
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][log_source] == "snort_ids" {
    json {
      source => "message"
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    geoip {
      source => "src_ip"
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "snort-alerts-%{+YYYY.MM.dd}"
  }
}
```

### Kibana Dashboard

Create visualizations for:
- Alert counts over time
- Top source IPs
- Top attack types
- Geographic distribution of attacks

---

## Monitoring and Maintenance

### Health Checks

```bash
# Check container status
docker-compose ps

# View Snort logs
docker logs snort-ids --tail 100

# Check disk usage
df -h /mnt/hdd/snort/logs
```

### Log Rotation

Logs are automatically rotated by Snort. For additional management:

```bash
# Add to crontab for weekly cleanup
0 0 * * 0 find /mnt/hdd/snort/logs -name "*.log.*" -mtime +30 -delete
```

### Rule Updates

```bash
# Update rules periodically
docker-compose exec snort pulledpork.pl -c /etc/snort/pulledpork.conf

# Restart Snort to apply new rules
docker-compose restart snort
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check network interface name in docker-compose.yml |
| No alerts generated | Verify network_mode: host is set |
| Permission denied | Ensure /mnt/hdd/snort/logs is writable |
| High CPU usage | Adjust detection_filter thresholds |

---

## References

- [Snort Official Documentation](https://www.snort.org/documents)
- [Snort Rule Writing Guide](https://www.snort.org/documents/snort-rule-writing)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## License

This project is for educational purposes as part of a cybersecurity portfolio.