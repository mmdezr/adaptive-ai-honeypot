# Deployment Guide

## Requirements
- Rocky Linux 9
- Podman
- At least 8 GB RAM recommended

## Network
All services are connected to an isolated Podman network (`elknet`).

## Cowrie
1. Build the container using `cowrie/build/Containerfile`
2. Mount runtime configuration from `cowrie/runtime/etc`
3. Expose SSH honeypot port (typically redirected from 22)

## ELK Stack
- Elasticsearch: stores honeypot events
- Logstash: parses and enriches Cowrie logs
- Filebeat: ships logs to Logstash
- Kibana: visualization

GeoIP databases must be downloaded manually (see `elk/logstash/GeoIP/README.md`).

## Secrets
Credentials are injected via environment variables:
- `ELASTIC_PASSWORD`

Never commit secrets to the repository.

