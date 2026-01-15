#!/bin/bash
set -e

# Enable APOC file import
echo "apoc.import.file.enabled=true" >> /var/lib/neo4j/conf/apoc.conf
echo "apoc.import.file.use_neo4j_config=true" >> /var/lib/neo4j/conf/apoc.conf

# Start Neo4j in the background
/startup/docker-entrypoint.sh neo4j &

# Wait for Neo4j to be available
echo "Waiting for Neo4j to start..."
until cypher-shell -u ${WRAPPER_USER} -p ${WRAPPER_PASS} "RETURN 1" >/dev/null 2>&1; do
  sleep 2
done

echo "Neo4j is up. Running initialization scripts..."

# Run init.cypher
# echo "Running init.cypher..."
# cypher-shell -u ${WRAPPER_USER} -p ${WRAPPER_PASS} -f /var/lib/neo4j/import/init.cypher || echo "init.cypher failed (might not exist)"

# Run load.cypher
echo "Running neo4j-load.cypher..."
cypher-shell -u ${WRAPPER_USER} -p ${WRAPPER_PASS} -f /var/lib/neo4j/import/neo4j-load.cypher || echo "neo4j-load.cypher failed"

echo "Initialization complete. Tailing logs..."
wait
