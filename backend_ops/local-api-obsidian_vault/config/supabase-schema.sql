-- Supabase Schema for AI Agent Retrieval Logic
-- Run this in your Supabase SQL Editor

-- Agent Contexts Table
CREATE TABLE IF NOT EXISTS agent_contexts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id TEXT NOT NULL UNIQUE,
    context JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Retrieval Cache Table
CREATE TABLE IF NOT EXISTS retrieval_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    query TEXT NOT NULL,
    results JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Interaction Logs
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_contexts_agent_id ON agent_contexts(agent_id);
CREATE INDEX IF NOT EXISTS idx_retrieval_cache_query ON retrieval_cache(query);
CREATE INDEX IF NOT EXISTS idx_retrieval_cache_created_at ON retrieval_cache(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);

-- RLS Policies (optional - enable if you need row-level security)
-- ALTER TABLE agent_contexts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE retrieval_cache ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

-- Auto-update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for agent_contexts
CREATE TRIGGER update_agent_contexts_updated_at 
    BEFORE UPDATE ON agent_contexts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();