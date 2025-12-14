# Adaptive AI Honeypots for Corporate Networks

This project implements an **adaptive honeypot system** designed for corporate-style environments.
It combines deception technologies (SSH honeypot) with data-driven decision making using
machine learning and contextual bandits.

The system dynamically adapts the behavior of the honeypot in response to attacker activity,
with the goal of increasing engagement time and improving threat intelligence collection.

---

## System Architecture

The solution is composed of four main layers:

1. **Deception Layer**
   - SSH honeypot based on Cowrie
   - Multiple deception profiles (conservative, convincing, vulnerable)
   - Containerized deployment using Podman on Rocky Linux

2. **Observation & Telemetry**
   - Cowrie logs collected in JSON format
   - Filebeat for log shipping
   - Logstash for parsing, enrichment and normalization
   - Elasticsearch for storage and querying
   - Kibana for visualization and analysis

3. **AI & Decision Layer**
   - Random Forest classifier for session/state characterization
   - LinUCB contextual bandit for adaptive profile selection
   - Reward functions based on attacker interaction metrics

4. **Adaptation Layer**
   - Runtime profile switching in Cowrie
   - Feedback loop driven by observed attacker behavior

---

## Repository Structure

cowrie/ # Cowrie container build and runtime configuration
elk/ # Filebeat and Logstash pipeline (GeoIP, parsing, enrichment)
ia/ # Machine learning, adaptation logic and analysis scripts
scripts/ # Deployment and synchronization utilities
docs/ # Security, deployment and design documentation


---

## Machine Learning Approach

### State Classification (Random Forest)
Each attacker session is characterized using features extracted from Cowrie logs, such as:
- Session duration
- Command frequency
- Download activity
- IP reuse patterns

A Random Forest model is used due to its robustness, interpretability and low inference cost.

### Decision Policy (LinUCB)
Profile selection is modeled as a **contextual bandit problem**:
- Context: classified session state
- Actions: available deception profiles
- Reward: engagement-oriented metrics

LinUCB was chosen to balance exploration and exploitation while remaining computationally lightweight.

---

## Deployment Overview

- Operating system: Rocky Linux
- Container runtime: Podman
- Services:
  - Cowrie (SSH honeypot)
  - Elasticsearch
  - Logstash
  - Filebeat
  - Kibana

Secrets (e.g., Elasticsearch credentials) are injected via environment variables
and are **never stored in the repository**.

See:
- `docs/DEPLOYMENT.md`
- `docs/SECURITY.md`

---

## Security and Ethics

This project is intended **strictly for controlled environments** (research, education, internal monitoring).
It must not be deployed on production systems without proper authorization.

The repository excludes:
- Real attacker datasets
- Malware samples
- Credentials or private keys
- GeoIP databases

---

## Academic Context

This project was developed as part of a Bachelor's Final Project (TFG),
focusing on cybersecurity, threat intelligence and applied machine learning.

