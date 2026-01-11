-- SalesMCP Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    region TEXT
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    risk_score FLOAT DEFAULT 0.0,
    region TEXT
);

-- Deals table
CREATE TABLE IF NOT EXISTS deals (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    owner_id INT REFERENCES users(id),
    deal_value FLOAT NOT NULL,
    stage TEXT NOT NULL,
    probability FLOAT DEFAULT 0.0,
    expected_close_date DATE,
    last_activity DATE DEFAULT CURRENT_DATE
);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    deal_id INT REFERENCES deals(id),
    activity_type TEXT NOT NULL,
    activity_date DATE DEFAULT CURRENT_DATE,
    notes TEXT
);

-- Policies table
CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    policy_name TEXT NOT NULL,
    rule TEXT NOT NULL
);

-- Agent decisions table for audit and business memory
CREATE TABLE IF NOT EXISTS agent_decisions (
    id SERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    input_question TEXT NOT NULL,
    recommendation TEXT,
    confidence FLOAT,
    evidence JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_deals_owner ON deals(owner_id);
CREATE INDEX IF NOT EXISTS idx_deals_customer ON deals(customer_id);
CREATE INDEX IF NOT EXISTS idx_activities_deal ON activities(deal_id);
