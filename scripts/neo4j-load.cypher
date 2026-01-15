// Load JSON export and create Site nodes and LINK relationships
CALL apoc.load.json('file:///neo4j_query_table_data_2025-12-28.json') YIELD value
UNWIND value AS row
WITH row.p AS p
MERGE (s:Site {id: p.start.properties.id})
SET s += p.start.properties
MERGE (e:Site {id: p.end.properties.id})
SET e += p.end.properties
UNWIND p.segments AS seg
MERGE (a:Site {id: seg.start.properties.id})
SET a += seg.start.properties
MERGE (b:Site {id: seg.end.properties.id})
SET b += seg.end.properties
MERGE (a)-[r:LINK {id: seg.relationship.properties.id}]->(b)
SET r += seg.relationship.properties
RETURN count(*) AS imported;
