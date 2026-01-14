-- This script sets up the database schema for the topology agent,
-- including tables for network inventory and vector embeddings.

-- Define custom types for better data integrity
CREATE TYPE circuit_layer AS ENUM ('L1', 'L2', 'L3', 'OTS');
CREATE TYPE circuit_status AS ENUM ('up', 'down', 'maintenance', 'planned');

CREATE TABLE IF NOT EXISTS inventory_sites (
    id       TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    region   TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS inventory_circuits (
    id         TEXT PRIMARY KEY,
    src_site   TEXT NOT NULL REFERENCES inventory_sites(id) ON DELETE RESTRICT,
    dst_site   TEXT NOT NULL REFERENCES inventory_sites(id) ON DELETE RESTRICT, CHECK (src_site <> dst_site),
    layer      circuit_layer NOT NULL,
    status     circuit_status NOT NULL,
    metadata   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_inventory_circuits_src_dst_layer
    ON inventory_circuits (src_site, dst_site, layer);

CREATE INDEX IF NOT EXISTS idx_inventory_circuits_src_dst
    ON inventory_circuits (src_site, dst_site);

INSERT INTO inventory_sites (id, name, region, metadata) VALUES
  ('A', 'Dallas POP',    'US-South', '{"city": "Dallas"}'),
  ('B', 'Houston POP',   'US-South', '{"city": "Houston"}'),
  ('C', 'Austin POP',    'US-South', '{"city": "Austin"}'),
  ('D', 'San Antonio',   'US-South', '{"city": "San Antonio"}'),
  ('E', 'El Paso POP',   'US-South', '{"city": "El Paso"}')
ON CONFLICT (id) DO NOTHING;

INSERT INTO inventory_circuits (id, src_site, dst_site, layer, status, metadata) VALUES
  ('CIR-A-B-1', 'A', 'B', 'L2', 'up', '{"bandwidth": "10G", "provider": "Internal"}'),
  ('CIR-B-C-1', 'B', 'C', 'L2', 'up', '{"bandwidth": "10G"}'),
  ('CIR-C-D-1', 'C', 'D', 'L2', 'up', '{"bandwidth": "10G"}'),
  ('CIR-D-E-1', 'D', 'E', 'L2', 'up', '{"bandwidth": "10G"}'),
  ('CIR-A-D-1', 'A', 'D', 'L2', 'up', '{"bandwidth": "40G", "role": "backbone"}'),
  ('CIR-A-B-L3-1', 'A', 'B', 'L3', 'up', '{"bandwidth": "1G"}')
ON CONFLICT (id) DO NOTHING;


-- Check to see if pgvector is available
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Use a dimension that matches your embedding model.
-- For OpenAI text-embedding-3-large, dim = 3072
-- For text-embedding-3-small, dim = 1536
-- Adjust as needed.
CREATE TABLE IF NOT EXISTS comment_embeddings (
    comment_id TEXT PRIMARY KEY,
    embedding  VECTOR(768),
    metadata   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_comment_embeddings_embedding
    ON comment_embeddings
    USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);



INSERT INTO comment_embeddings (comment_id, embedding, metadata) VALUES
  (
    'CMT-1',
    zeros(768),
    '{"text": "Fiber cut reported between A and D last week", "ticket_id": "TKT-123"}'
  )
ON CONFLICT (comment_id) DO NOTHING;