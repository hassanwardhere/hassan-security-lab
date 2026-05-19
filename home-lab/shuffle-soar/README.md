# Shuffle SOAR Deployment

**Author:** Hassan Abdulahi Hassan  
**Date:** May 19, 2026  
**Purpose:** Security Orchestration, Automation and Response platform integrated with Wazuh and Snort

---

## Deployment Status

**Status:** Configuration Complete, Images Pending Authentication

Shuffle SOAR requires GitHub Container Registry (ghcr.io) authentication to pull the official images. The deployment configuration is complete and ready to launch once authentication is resolved.

---

## Architecture Overview

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Wazuh Manager  │─────▶│  Shuffle Backend  │────▶│  OpenSearch DB   │
│   (Alerts)      │     │    (API:5001)    │     │   (Data Store)  │
└─────────────┘     └───────┬─────────────┘     └─────────────────┘
                      │
       ┌─────────────────┐      │
       │ Shuffle Frontend  │◀────┬─────────────┐
       │   (Web UI:3443)   │      │  Orborus Worker  │
       └─────────────────┘      │   (Executions)   │
                                      └─────────────────┘
```

---

## Configuration

### Services

| Service | Image Source | Port | Purpose |
|---------|-------------|------|---------|
| Frontend | ghcr.io/shuffle/shuffle-frontend | 3443 | Web UI |
| Backend | ghcr.io/shuffle/shuffle-backend | 5001 | API Server |
| Orborus | ghcr.io/shuffle/shuffle-orborus | - | Workflow Executor |
| OpenSearch | opensearchproject/opensearch:3.2.0 | 9200 | Database |

### Planned Integrations

1. **Wazuh Integration**
   - API endpoint: https://single-node-wazuh.manager-1:55000
   - Authentication: wazuh-wui user
   - Alert types: SSH brute force, port scans, file integrity

2. **Snort Integration**
   - Log path: /mnt/hdd/snort/logs/alert.json
   - Alert types: SQL injection, XSS, port scans

3. **ELK Stack Integration**
   - Elasticsearch: http://elasticsearch:9201
   - For enriched alerting and correlation

---

## Deployment Steps

### Prerequisites

GitHub Personal Access Token with `read:packages` scope is required to pull images from ghcr.io.

```bash
# Authenticate to GitHub Container Registry
echo "YOUR_GHCR_TOKEN" | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### Deployment Commands

```bash
# Clone Shuffle repository
git clone https://github.com/shuffle/shuffle.git
cd shuffle

# Configure environment
cp .env .env.local
# Edit FRONTEND_PORT_HTTPS=3443 and other settings

# Create directories
mkdir -p shuffle-apps shuffle-files shuffle-database

# Deploy
docker compose up -d
```

---

## Automated Response Workflow Design

### Workflow: Brute Force Response

**Trigger:** Wazuh alert level 10+ (SSH brute force detected)

**Actions:**
1. Parse alert to extract attacker IP
2. Query Wazuh for additional context
3. Block IP via iptables/ufw
4. Create incident ticket
5. Send notification via Telegram
6. Log action to ELK Stack

**Apps Required:**
- Wazuh (installed)
- SSH/Terminal (for iptables)
- Telegram (for notifications)
- HTTP (for ELK logging)

---

## Access Information

Once deployed:
- **Web UI:** https://localhost:3443
- **Backend API:** http://localhost:5001
- **OpenSearch:** https://localhost:9200

Default credentials configured in .env file.

---

## Troubleshooting

### Issue: Image Pull Authentication Failed

**Error:** `denied: denied` when pulling from ghcr.io

**Solution:**
1. Generate GitHub Personal Access Token with `read:packages` scope
2. Authenticate: `docker login ghcr.io -u USERNAME`
3. Enter token as password

### Issue: Port Already in Use

**Solution:**
Shuffle frontend uses port 3443 (HTTPS) by default.
Backend API uses port 5001.
OpenSearch uses port 9200.

Check port availability before deployment.

---

## Next Steps

1. Obtain GitHub PAT with package read permissions
2. Authenticate to ghcr.io
3. Deploy Shuffle: `docker compose up -d`
4. Configure Wazuh API connection
5. Configure Snort log ingestion
6. Build brute force response workflow
7. Test end-to-end automation

---

## References

- [Shuffle Documentation](https://shuffler.io/docs)
- [Shuffle GitHub](https://github.com/shuffle/shuffle)
- [Wazuh API Documentation](https://documentation.wazuh.com/current/user-manual/api/index.html)
