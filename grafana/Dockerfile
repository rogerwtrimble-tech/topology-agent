FROM grafana/grafana:10.2.0

# Copy dashboard JSON files into the default provisioning path for dashboards
# Use --chown to set the owner to the grafana user (uid:gid 472:472)
COPY --chown=472:472 ./scripts/ /var/lib/grafana/dashboards/

# Copy provisioning configuration for datasources and dashboards
COPY --chown=472:472 ./grafana/provisioning/ /etc/grafana/provisioning/