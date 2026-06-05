# Hassan Security Lab — Personal Cybersecurity Homelab

This is a personal SOC learning environment built to practice detection engineering on Ubuntu Desktop 24.04. It runs open-source security tooling on a single laptop in my home network, and exists so I can get hands-on experience with SIEM deployment, log onboarding, rule writing, and incident triage outside of coursework.

---

## Hardware

| Component | Details |
|-----------|---------|
| Device | HP Envy laptop |
| CPU | AMD A12-9720P (4 cores) |
| RAM | 14 GB |
| Storage | 256 GB NVMe SSD (root) + 1 TB HDD |
| HDD mount | `/mnt/hdd` |
| OS | Ubuntu Desktop 24.04 |

---

## Status

| Tool | Status | Notes |
|------|--------|-------|
| Wazuh 4.14.5 (single-node) | ✅ Deployed | Manager + Indexer + Dashboard via official docker-compose, data on HDD |
| ELK Stack | ✅ Deployed | Elasticsearch + Logstash + Kibana, integrated with Wazuh |
| Snort IDS | ✅ Deployed | 46 custom detection rules |
| Shuffle SOAR | ✅ Deployed | Automation workflows, Wazuh + MISP integration |
| MISP Threat Intel | ✅ Deployed | Live at port 8080, Wazuh CDB integration documented |
| Velociraptor EDR | ✅ Deployed | Docker compose config, documentation complete |
| Vulnerability Scanner | ✅ Deployed | TCP port scanner with CVE lookup via NVD API |
| Log Analysis Automation | ✅ Deployed | Parses auth logs, detects SSH brute force attempts |

---

## Wazuh Deployment

Wazuh is deployed as a single-node stack using the official [wazuh-docker](https://github.com/wazuh/wazuh-docker) repository, pinned to tag **v4.14.5**. Three containers run: `wazuh.manager`, `wazuh.indexer`, and `wazuh.dashboard`. The dashboard is reachable at `https://192.168.3.71` on the host LAN.

**Docker data root migrated to HDD.** The default `/var/lib/docker` location lives on the 256 GB SSD, which is too small for indexer data over time. Docker's data root was moved to `/mnt/hdd/docker/data` by editing `/etc/docker/daemon.json`:

```
{
  "data-root": "/mnt/hdd/docker/data"
}
```

Existing images and volumes were rsynced over before restarting the Docker service.

**Kernel parameter for the indexer.** The Wazuh indexer (OpenSearch) requires a higher `vm.max_map_count` than the Ubuntu default. Set persistently in `/etc/sysctl.d/99-wazuh.conf`:

```
vm.max_map_count=262144
```

Applied with `sudo sysctl --system`.

---

## Automation Tools

### Vulnerability Scanner
A TCP port scanner with service detection and CVE lookup. Scans targets for open ports, fingerprints services via banner grabbing, and queries the NVD API for known vulnerabilities. See [home-lab/vulnerability-scanner/](home-lab/vulnerability-scanner/README.md).

### Log Analysis Automation
Parses system authentication logs to detect SSH brute force attempts. Groups failed logins by source IP, flags IPs exceeding configurable thresholds, and generates markdown reports. See [home-lab/log-analysis/](home-lab/log-analysis/README.md).

---

## What I'm Currently Learning

- Detection engineering and rule writing in Wazuh
- Log source onboarding and correlation
- MITRE ATT&CK framework mapping
- Threat intelligence with MISP
- Endpoint detection with Velociraptor
- SOAR workflow development with Shuffle
- Scripting security automation in Python

---

## About

Hassan Abdulahi Hassan — BSc Computing, University of Greenwich (April 2026). Based in Nairobi, Kenya.
