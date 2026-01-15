// Simple topology seed for Dallas POP and San Antonio
MERGE (d:Dc {name: 'Dallas POP', region: 'Dallas'})
MERGE (s:Dc {name: 'San Antonio', region: 'San Antonio'})
MERGE (d)-[r:CONNECTED_TO {layer: 'L2', status: 'active'}]->(s)

// Add an example outage event related to the Dallas-SanAntonio link
CREATE (o:Outage {id: randomUUID(), description: 'Test outage on Dallas-San Antonio link', severity: 'major', start: timestamp()})
MERGE (o)-[:AFFECTS]->(d)
MERGE (o)-[:AFFECTS]->(s)

RETURN 'ok';
