# MISP Threat Intelligence Platform

## What is MISP?

MISP (Malware Information Sharing Platform & Threat Sharing) is an open-source threat intelligence platform designed to improve the sharing of structured threat information. It allows security teams to collect, share, store, and correlate indicators of compromise (IOCs), threat actors, malware samples, and other threat intelligence data.

## Why MISP in the Homelab?

MISP serves as the central threat intelligence hub in this SOC learning environment:

- **IOC Management**: Store and organize indicators of compromise (IPs, domains, file hashes) for detection rules
- **Threat Intelligence**: Subscribe to global threat feeds to stay current on emerging threats
- **Wazuh Integration**: Feed MISP threat intelligence into Wazuh for automated detection and alerting
- **Incident Correlation**: Correlate security events against known threat intelligence
- **Learning Platform**: Practice threat intelligence analysis and sharing workflows

## Architecture

```
├── MISP Web Application (port 8080)
│   └── Harvard IT Security MISP Docker image
├── MySQL Database (internal)
│   └── Stores events, attributes, users
└── Wazuh Integration (planned)
    └── API queries for threat intel lookups
```

## Deployment

### Prerequisites

- Docker and Docker Compose installed
- HDD mounted at `/mnt/hdd` for persistent storage (Docker volumes)
- Port 8080 available on the host

### Setup

1. Copy the environment file and configure:

```bash
cp .env.example .env
nano .env  # Edit passwords and URLs
```

2. Start MISP:

```bash
docker compose up -d
```

3. Access MISP at `http://192.168.3.71:8080`
   - Default login: admin@admin.test / changeme (change immediately)

4. Wait for the initialization to complete (database setup takes ~2-3 minutes on first run)

### First-Time Configuration

1. **Change Admin Password**: Login and update the default password
2. **Configure Organization**: Set up your organization name and UUID
3. **Enable Feeds**: Navigate to Sync Actions → List Feeds and enable relevant threat feeds
4. **Set Base URL**: Ensure MISP_BASEURL matches your LAN IP

## Wazuh Integration

MISP integrates with Wazuh through the Wazuh API and custom rules:

### How It Works

1. **Threat Intel Lookup**: Wazuh queries MISP API to check if observed IPs, domains, or file hashes match known IOCs
2. **Automatic Enrichment**: Security alerts are enriched with threat intelligence context from MISP
3. **Correlation**: Events correlated with MISP IOCs generate higher-priority alerts

### Integration Configuration

1. **Wazuh Manager Configuration**: Add MISP API credentials to Wazuh's `ossec.conf`:

```xml
<integration>
  <name>misp</name>
  <hook_url>http://192.168.3.71:8080/events/restSearch</hook_url>
  <api_key>YOUR_MISP_API_KEY</api_key>
  <alert_format>json</alert_format>
</integration>
```

2. **Network Connectivity**: Both containers run on the host network for API communication

3. **Custom Rules**: Wazuh rules reference MISP data for threat detection

## Current Status

**Deployment in progress — database config issue being resolved**

The MISP Docker container is starting but encountering a database authentication issue. The container is attempting to connect as user 'apache' instead of the configured 'misp' user. Troubleshooting the database configuration.
|-----------|--------|-------|
| MISP Core | ✅ Deployed | Running on port 8080 |
| MySQL Database | ✅ Deployed | Docker volume for persistence |
| Wazuh Integration | ⏳ In Progress | API configuration pending |
| Threat Feeds | ⏳ In Progress | Default feeds enabled, custom feeds planned |

## Next Steps

- [ ] Configure Wazuh API integration for automated lookups
- [ ] Subscribe to premium threat feeds (CIRCL, abuse.ch)
- [ ] Create custom warning lists for false positive reduction
- [ ] Set up automated IOC export to Wazuh CDB lists
- [ ] Configure email alerts for high-confidence IOC matches

## Resources

- [MISP Official Documentation](https://www.circl.lu/doc/misp/)
- [MISP Docker GitHub](https://github.com/HASecuritySolutions/misp-docker)
- [Wazuh MISP Integration Guide](https://documentation.wazuh.com/current/user-manual/capabilities/malware-detection/misp-integration.html)

## Directory Structure

```
misp/
├── README.md              # This documentation
├── docker-compose.yml     # Container orchestration
└── .env.example          # Environment configuration template
```
