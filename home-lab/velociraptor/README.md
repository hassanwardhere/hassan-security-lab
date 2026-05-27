# Velociraptor EDR Platform

## What is Velociraptor?

Velociraptor is an advanced digital forensics and incident response (DFIR) platform that provides endpoint detection, monitoring, and response capabilities. Originally developed by Rapid7, it's now an open-source project that gives security teams deep visibility into endpoints through:

- **Velociraptor Query Language (VQL)**: A powerful query language for hunting and collecting forensic artifacts
- **Real-time endpoint monitoring**: Collect telemetry from endpoints at scale
- **Artifact collection**: Pre-built and custom forensic artifacts for threat hunting
- **Remote response capabilities**: Execute responses across endpoints from a central console

## Why Velociraptor in the Homelab?

As an EDR (Endpoint Detection and Response) platform, Velociraptor serves several critical functions in this security lab:

1. **Centralized Endpoint Telemetry**: Collects detailed forensic data from all lab endpoints (Windows, Linux, macOS)
2. **Threat Hunting**: Use VQL to hunt for indicators of compromise (IOCs) across the entire fleet
3. **Incident Response**: Rapid investigation and response to simulated security incidents
4. **DFIR Training**: Hands-on practice with enterprise-grade forensic tooling
5. **SIEM Integration**: Feeds normalized telemetry into Wazuh for correlation and alerting

## Docker Compose Configuration

```yaml
version: '3.8'

services:
  velociraptor:
    image: rapid7/velociraptor:latest
    container_name: velociraptor-server
    hostname: velociraptor
    restart: unless-stopped
    ports:
      - "8889:8889"    # GUI
      - "8000:8000"    # API
      - "8001:8001"    # Frontend
    volumes:
      - ./config:/config:ro
      - ./data:/data
      - ./logs:/logs
    environment:
      - VELOCIRAPTOR_CONFIG=/config/server.config.yaml
    networks:
      - security-lab

networks:
  security-lab:
    external: true
    name: security-lab-network
```

### Deployment Notes

- **Data Persistence**: Mount volumes for config, data, and logs
- **Network**: Connects to shared security-lab-network for service communication
- **Ports**: 8889 (web GUI), 8000 (API), 8001 (client communication)

## Wazuh Integration

Velociraptor integrates with Wazuh to provide comprehensive endpoint telemetry:

### Data Flow

```
Endpoints → Velociraptor Server → Filebeat/Logstash → Wazuh Indexer
```

### Integration Points

1. **Log Forwarding**: Velociraptor logs forwarded via Filebeat to Wazuh
2. **Alert Correlation**: VQL hunt results correlate with Wazuh alerts
3. **Enrichment**: Velociraptor artifact data enriches Wazuh security events
4. **Response Actions**: Wazuh active responses trigger Velociraptor hunts

### Configuration Example

```yaml
# Filebeat configuration for Velociraptor logs
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/velociraptor/*.log
    fields:
      service: velociraptor
      type: edr
    fields_under_root: true
```

## Current Deployment Status

| Component | Status | Notes |
|-----------|--------|-------|
| Velociraptor Server | Planned | Docker compose configured, pending deployment |
| Client Deployment | Planned | Windows/Linux agents to be deployed post-server |
| Wazuh Integration | Planned | Filebeat pipeline configuration in progress |
| Initial Hunt | Pending | Baseline VQL hunts after full deployment |

### Next Steps

1. Deploy Velociraptor server container
2. Generate and deploy client configurations
3. Configure Filebeat for log forwarding to Wazuh
4. Create initial VQL hunt library for common threats
5. Document incident response playbooks

## Resources

- [Velociraptor Documentation](https://docs.velociraptor.app/)
- [VQL Reference](https://docs.velociraptor.app/vql_reference/)
- [Artifact Exchange](https://docs.velociraptor.app/exchange/)
- [GitHub Repository](https://github.com/Velocidex/velociraptor)
