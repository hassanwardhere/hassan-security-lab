# Hassan's Cybersecurity Home Lab

## Overview

This repository documents the design, deployment, and operation of a 
personal cybersecurity home lab built from the ground up on Ubuntu 24.04 
LTS. The lab simulates a real-world Security Operations Centre (SOC) 
environment, providing hands-on experience with industry-standard open 
source security tools used by professionals across MSSP, banking, and 
enterprise environments.

Every tool deployed here mirrors what is expected in roles such as SOC 
Analyst, Cybersecurity Engineer, and IT Risk Officer positions across 
Kenya, East Africa, and Europe.

---

## Hardware Specifications

| Component | Details                          |
|-----------|----------------------------------|
| Device    | HP Envy Laptop                   |
| CPU       | AMD A12-9720P, 4 Cores           |
| RAM       | 16GB                             |
| Storage   | 256GB SSD (OS) + 1TB HDD (Data)  |
| OS        | Ubuntu 24.04.4 LTS               |
| Network   | Ethernet + WiFi                  |

---

## Architecture

All tools run as isolated Docker containers managed through Portainer. 
Container data and logs are stored on the 1TB HDD mounted at /mnt/hdd 
to preserve SSD lifespan and maximise storage capacity.
┌─────────────────────────────────────────┐
│           Ubuntu 24.04 LTS              │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │         Docker Engine           │    │
│  │                                 │    │
│  │  ┌──────────┐  ┌─────────────┐  │    │
│  │  │  Wazuh   │  │  ELK Stack  │  │    │
│  │  │  (SIEM)  │  │  (Logging)  │  │    │
│  │  └──────────┘  └─────────────┘  │    │
│  │                                 │    │
│  │  ┌──────────┐  ┌─────────────┐  │    │
│  │  │  Snort   │  │Velociraptor │  │    │
│  │  │ (IDS/IPS)│  │   (EDR)     │  │    │
│  │  └──────────┘  └─────────────┘  │    │
│  │                                 │    │
│  │  ┌──────────┐  ┌─────────────┐  │    │
│  │  │ Shuffle  │  │    MISP     │  │    │
│  │  │  (SOAR)  │  │(Threat Intel│  │    │
│  │  └──────────┘  └─────────────┘  │    │
│  │                                 │    │
│  │  ┌──────────────────────────┐   │    │
│  │  │    Portainer (Manager)   │   │    │
│  │  └──────────────────────────┘   │    │
│  └─────────────────────────────────┘    │
│                                         │
│  SSD: OS + Docker    HDD: All Data      │
└─────────────────────────────────────────┘

---

## Tools Deployed

| Tool          | Category          | Purpose                                      | Status      |
|---------------|-------------------|----------------------------------------------|-------------|
| Docker        | Infrastructure    | Container engine for all tools               | ✅ Complete |
| Portainer     | Infrastructure    | Visual Docker management interface           | ✅ Complete |
| Wazuh         | SIEM              | Security event monitoring and alerting       | 🔄 In Progress |
| ELK Stack     | Log Analysis      | Log ingestion, search, and visualisation     | ⏳ Pending  |
| Snort         | IDS/IPS           | Network intrusion detection and prevention   | ⏳ Pending  |
| Velociraptor  | EDR               | Endpoint detection and response              | ⏳ Pending  |
| Shuffle       | SOAR              | Security orchestration and automated response| ⏳ Pending  |
| MISP          | Threat Intel      | Malware information sharing and threat feeds | ⏳ Pending  |

---

## Repository Structure
hassan-security-lab/
├── README.md                  ← You are here
├── setup/
│   ├── docker-setup.md        ← Docker and Portainer installation
│   └── screenshots/           ← Terminal and UI screenshots
├── wazuh/
│   ├── README.md              ← Wazuh deployment and configuration
│   ├── config/                ← Docker compose and config files
│   └── screenshots/
├── elk-stack/
│   ├── README.md
│   ├── config/
│   └── screenshots/
├── snort/
│   ├── README.md
│   ├── config/
│   └── screenshots/
├── velociraptor/
│   ├── README.md
│   ├── config/
│   └── screenshots/
├── shuffle/
│   ├── README.md
│   ├── config/
│   └── screenshots/
└── misp/
├── README.md
├── config/
└── screenshots/

---

## Skills Demonstrated

- Docker containerisation and orchestration
- SIEM deployment, configuration, and rule tuning
- Network intrusion detection and alert analysis
- Endpoint detection and incident investigation
- Log ingestion, parsing, and visualisation
- Security orchestration and automated response
- Threat intelligence integration and feed management
- Incident documentation and reporting

---

## Certifications In Progress

- CompTIA Security+ (SY0-701)

---

## About

Built by Hassan — University of Greenwich graduate in Cybersecurity.  
Targeting SOC Analyst, Security Engineer, and IT Risk roles across  
Kenya, South Africa, and Europe.

GitHub: [hassanwardhere](https://github.com/hassanwardhere)  
LinkedIn: https://www.linkedin.com/in/hassan-abdullahi-/  
Portfolio: [hassanahassan.com](https://hassanahassan.com)