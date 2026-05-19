# ELK Stack SIEM Integration

**Author:** Hassan Abdulahi Hassan  
**Date:** May 19, 2026  
**Purpose:** Centralized log aggregation and analysis for Wazuh security events

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Wazuh Manager │────▶│   Filebeat   │────▶│   Logstash   │────▶│Elasticsearch │
│   (Existing)    │     │  (Shipper)   │     │ (Processor)  │     │  (Storage)   │
└─────────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                          │
                                                                          ▼
                                                                   ┌──────────────┐
                                                                   │    Kibana    │
                                                                   │(Visualization)│
                                                                   └──────────────┘
```

---

## Components

| Service | Version | Port | Purpose |
|---------|---------|------|---------|
| Elasticsearch | 8.11.0 | 9201 | Log storage and search engine |
| Logstash | 8.11.0 | 5044 (Beats), 9600 (API) | Log parsing and enrichment |
| Kibana | 8.11.0 | 5601 | Visualization and dashboards |
| Filebeat | 8.11.0 | - | Log shipper from Wazuh |

---

## Deployment

### Network Configuration

Created dedicated Docker network for isolation:
```bash
docker network create elk-stack
```

### Port Mapping

- **Elasticsearch:** 9201 (avoiding conflict with Temporal on 9200)
- **Logstash:** 5044 (Beats input), 9600 (monitoring API)
- **Kibana:** 5601 (web interface)

### Logstash Pipeline

**Input:** Beats on port 5044  
**Processing:**
- Parse Wazuh JSON alerts
- Extract rule information (level, description, ID)
- Categorize by log type (file_integrity, rootkit_detection, security_alert)
- Add severity classification (critical/high/medium/low)
- Timestamp normalization

**Output:** Elasticsearch index `wazuh-logs-%{+YYYY.MM.dd}`

### Filebeat Configuration

**Inputs:**
1. `/var/ossec/logs/alerts/alerts.json` — Wazuh alerts
2. `/var/ossec/logs/archives/*.json` — Archived logs

**Output:** Logstash at `logstash:5044`

---

## Wazuh Integration

### Data Flow

1. Wazuh Manager generates alerts in `/var/ossec/logs/alerts/alerts.json`
2. Filebeat reads and ships logs via Docker volume mount:
   ```
   /mnt/hdd/docker/data/volumes/single-node_wazuh_logs/_data:/var/ossec/logs:ro
   ```
3. Logstash processes and enriches the data
4. Elasticsearch stores and indexes the logs
5. Kibana provides visualization interface

### Log Types Ingested

- **Security Alerts:** Rule-based detections from Wazuh
- **File Integrity:** Syscheck (FIM) events
- **Rootkit Detection:** Rootcheck scan results
- **System Archives:** All collected logs

---

## Access Information

| Endpoint | URL | Credentials |
|----------|-----|-------------|
| Kibana | http://localhost:5601 | None (security disabled for lab) |
| Elasticsearch | http://localhost:9201 | None |
| Logstash API | http://localhost:9600 | None |

---

## Verification Commands

```bash
# Check Elasticsearch cluster health
curl http://localhost:9201/_cluster/health

# List indices
curl http://localhost:9201/_cat/indices?v

# View indexed documents
curl http://localhost:9201/wazuh-logs-*/_search?pretty

# Check Kibana status
curl http://localhost:5601/api/status

# View Filebeat logs
docker logs filebeat
```

---

## Resource Allocation

| Service | Memory | CPU |
|---------|--------|-----|
| Elasticsearch | 2GB heap | Unlimited |
| Logstash | 1GB heap | Unlimited |
| Kibana | Default | Unlimited |
| Filebeat | Default | Unlimited |

---

## Screenshots

See `screenshots/` directory for:
- Kibana Discover interface
- Elasticsearch index management
- Log pipeline monitoring

---

## Next Steps

1. Create Kibana index patterns for `wazuh-logs-*`
2. Build dashboards for:
   - Alert severity overview
   - Top attack signatures
   - File integrity monitoring
   - Geographic attack distribution
3. Configure alerts and notifications
4. Integrate with Shuffle SOAR for automated response

---

## Troubleshooting

### Filebeat can't read Wazuh logs
Ensure the Docker volume mount path is correct:
```bash
docker inspect single-node-wazuh.manager-1 --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' | grep logs
```

### Logstash connection refused
Check that Logstash container is healthy and port 5044 is open:
```bash
docker logs logstash
telnet localhost 5044
```

### No data in Elasticsearch
Verify Filebeat is connected to Logstash:
```bash
docker logs filebeat | grep "Connection to backoff"
```

---

## References

- [Elastic Stack Documentation](https://www.elastic.co/guide/en/elastic-stack-get-started/current/get-started-elastic-stack.html)
- [Wazuh Documentation](https://documentation.wazuh.com/)
- [Filebeat Reference](https://www.elastic.co/guide/en/beats/filebeat/current/index.html)
