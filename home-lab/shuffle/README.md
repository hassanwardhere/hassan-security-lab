# Shuffle SOAR Platform

## What is Shuffle?

Shuffle is an open-source Security Orchestration, Automation and Response (SOAR) platform that streamlines security operations by automating repetitive tasks and coordinating responses across multiple security tools. Key capabilities include:

- **Visual Workflow Builder**: Drag-and-drop interface for creating automation playbooks
- **App Ecosystem**: 200+ pre-built integrations with security tools (SIEM, EDR, threat intel, etc.)
- **Case Management**: Track and manage security incidents from detection to resolution
- **API-First Architecture**: Everything is API-driven, enabling extensive customization
- **Self-Hosted**: Full data control with on-premises deployment

## Why Shuffle in the Homelab?

As the central orchestration layer, Shuffle automates incident response workflows:

1. **Automated Triage**: Filter and prioritize alerts from Wazuh before analyst review
2. **Threat Intel Enrichment**: Automatically query MISP and other sources for IOC context
3. **Response Automation**: Execute containment actions across endpoints and network
4. **Notification Workflows**: Route critical alerts to appropriate channels (email, Slack, etc.)
5. **Metrics & Reporting**: Track response times and measure SOC efficiency

## Docker Compose Configuration

```yaml
version: '3.8'

services:
  shuffle-backend:
    image: ghcr.io/shuffle/shuffle-backend:latest
    container_name: shuffle-backend
    hostname: shuffle-backend
    restart: unless-stopped
    ports:
      - "5001:5001"
    environment:
      - SHUFFLE_APP_DOWNLOAD_LOCATION=/shuffle-apps
      - SHUFFLE_ORG_ID=${SHUFFLE_ORG_ID}
      - SHUFFLE_OPENSEARCH_URL=http://shuffle-opensearch:9200
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./shuffle-apps:/shuffle-apps
      - ./data:/data
    networks:
      - security-lab
    depends_on:
      - shuffle-opensearch

  shuffle-frontend:
    image: ghcr.io/shuffle/shuffle-frontend:latest
    container_name: shuffle-frontend
    hostname: shuffle-frontend
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - BACKEND_HOSTNAME=shuffle-backend
      - BACKEND_PORT=5001
    networks:
      - security-lab
    depends_on:
      - shuffle-backend

  shuffle-opensearch:
    image: opensearchproject/opensearch:2.11.0
    container_name: shuffle-opensearch
    hostname: shuffle-opensearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g
      - plugins.security.disabled=true
    volumes:
      - ./opensearch-data:/usr/share/opensearch/data
    networks:
      - security-lab

  shuffle-orborus:
    image: ghcr.io/shuffle/shuffle-orborus:latest
    container_name: shuffle-orborus
    hostname: shuffle-orborus
    restart: unless-stopped
    environment:
      - SHUFFLE_APP_DOWNLOAD_LOCATION=/shuffle-apps
      - SHUFFLE_WORKER_NAME=worker
      - ORG_ID=${SHUFFLE_ORG_ID}
      - BASE_URL=http://shuffle-backend:5001
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./shuffle-apps:/shuffle-apps
    networks:
      - security-lab
    depends_on:
      - shuffle-backend

networks:
  security-lab:
    external: true
    name: security-lab-network
```

### Environment Variables

```bash
# .env file
SHUFFLE_ORG_ID=your-organization-id
```

## Wazuh Integration

Shuffle consumes Wazuh alerts via webhook/API and triggers automation workflows:

### Alert Ingestion

```
Wazuh Alerts → Shuffle Webhook → Workflow Trigger → Automated Response
```

### Integration Flow

1. **High-Severity Alerts**: Level 12+ alerts automatically create Shuffle cases
2. **Enrichment Pipeline**: IP/domain/file hashes enriched via MISP, VirusTotal
3. **Containment Actions**: Isolate hosts via Wazuh active response or firewall rules
4. **Notification**: Alert SOC team via email/Slack with enriched context

### Configuration

```python
# Shuffle workflow trigger - Wazuh webhook
{
  "name": "Wazuh Alert Handler",
  "trigger": "webhook",
  "webhook_uri": "/wazuh-alerts",
  "conditions": [
    {"field": "rule.level", "operator": ">=", "value": "12"}
  ]
}
```

## MISP Integration

Shuffle queries MISP for threat intelligence enrichment:

### Enrichment Workflow

1. Extract IOCs (IPs, hashes, domains) from Wazuh alerts
2. Query MISP for known malicious indicators
3. Update alert severity based on MISP confidence scores
4. Create incident case with full threat context

### Example Query Node

```python
# MISP app configuration in Shuffle
{
  "app": "MISP",
  "action": "search_events",
  "parameters": {
    "value": "{{alert.source_ip}}",
    "tags": ["tlp:amber"]
  }
}
```

## Example Playbooks

### Playbook 1: Malware Detection Response

**Trigger**: Wazuh detects malware signature

**Actions**:
1. Extract file hash from alert
2. Query VirusTotal and MISP for reputation
3. If malicious: 
   - Isolate endpoint via Wazuh
   - Create ticket in case management
   - Notify SOC team via Slack
4. Log all actions to Elasticsearch

### Playbook 2: Brute Force Attack Response

**Trigger**: Multiple failed login attempts detected

**Actions**:
1. Check source IP against MISP threat feed
2. If known malicious IP:
   - Block at firewall
   - Ban IP via fail2ban
3. Generate incident report
4. Alert security team

### Playbook 3: Phishing Investigation

**Trigger**: Email gateway reports suspicious email

**Actions**:
1. Extract URLs and attachments
2. Sandbox analysis via URLScan/VirusTotal
3. Query MISP for known phishing indicators
4. If confirmed phishing:
   - Search mailbox for similar emails
   - Delete/quarantine across organization
   - Update email gateway rules

## Current Deployment Status

| Component | Status | Notes |
|-----------|--------|-------|
| Shuffle Backend | Planned | Docker compose ready, pending Opensearch setup |
| Shuffle Frontend | Planned | Will deploy with backend |
| Opensearch | Planned | Database for workflow storage |
| Orborus Worker | Planned | Container executor for apps |
| Wazuh Webhook | Planned | Alert ingestion endpoint |
| MISP App | Planned | Threat intel app configuration |
| Initial Playbooks | Pending | Malware and brute force workflows |

### Next Steps

1. Deploy Shuffle stack with Docker Compose
2. Configure Wazuh webhook for alert ingestion
3. Set up MISP app with API credentials
4. Build initial malware detection playbook
5. Create brute force response automation
6. Document runbook procedures

## Resources

- [Shuffle Documentation](https://shuffler.io/docs)
- [Shuffle GitHub](https://github.com/shuffle/shuffle)
- [App Exchange](https://shuffler.io/apps)
- [Community Workflows](https://shuffler.io/workflows)
