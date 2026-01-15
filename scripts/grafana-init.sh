#!/bin/bash
set -e
# create provisioning dashboards dir and move dashboards.yml into it (if present)
mkdir -p /var/lib/grafana/dashboards
if [ -f /app/dashboards.yml ]; then
  mv /app/dashboards.yml /var/lib/grafana/dashboards/dashboards.yml
fi
echo "Grafana provisioning files ready."
