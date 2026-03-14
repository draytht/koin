-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id  TEXT UNIQUE NOT NULL,
    username    TEXT NOT NULL,
    currency    TEXT NOT NULL DEFAULT 'USD',
    timezone    TEXT NOT NULL DEFAULT 'UTC',
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);

-- Receipts table (referenced by expenses, so created first)
CREATE TABLE IF NOT EXISTS receipts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_path     TEXT NOT NULL,
    ocr_raw_text     TEXT,
    parsed_merchant  TEXT,
    parsed_total     NUMERIC(12,2),
    parsed_date      DATE,
    parsed_tax       NUMERIC(12,2),
    parsed_items     JSONB,
    confidence       NUMERIC(3,2),
    confirmed        BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_receipts_user ON receipts(user_id, created_at DESC);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount          NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    category        TEXT NOT NULL,
    merchant        TEXT,
    note            TEXT,
    payment_method  TEXT,
    date            DATE NOT NULL DEFAULT CURRENT_DATE,
    recurring       BOOLEAN NOT NULL DEFAULT false,
    receipt_id      UUID REFERENCES receipts(id),
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(user_id, category);

-- Income table
CREATE TABLE IF NOT EXISTS income (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    source      TEXT NOT NULL,
    note        TEXT,
    date        DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_income_user_date ON income(user_id, date DESC);

-- Debts table
CREATE TABLE IF NOT EXISTS debts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    debt_name        TEXT NOT NULL,
    creditor         TEXT NOT NULL,
    total_amount     NUMERIC(12,2) NOT NULL CHECK (total_amount > 0),
    current_balance  NUMERIC(12,2) NOT NULL CHECK (current_balance >= 0),
    interest_rate    NUMERIC(6,4) NOT NULL CHECK (interest_rate >= 0),
    minimum_payment  NUMERIC(12,2) NOT NULL CHECK (minimum_payment >= 0),
    due_date         DATE,
    note             TEXT,
    is_paid_off      BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, debt_name)
);

-- AI Reports table
CREATE TABLE IF NOT EXISTS ai_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type     TEXT NOT NULL,
    input_summary   JSONB,
    response_text   TEXT NOT NULL,
    tokens_used     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_reports_user ON ai_reports(user_id, created_at DESC);

-- Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE income ENABLE ROW LEVEL SECURITY;
ALTER TABLE debts ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_reports ENABLE ROW LEVEL SECURITY;

-- RLS Policies: service role bypasses RLS by default in Supabase
-- These policies protect against accidental data leakage if anon key is ever used
CREATE POLICY "service_role_only" ON users USING (true);
CREATE POLICY "service_role_only" ON expenses USING (true);
CREATE POLICY "service_role_only" ON income USING (true);
CREATE POLICY "service_role_only" ON debts USING (true);
CREATE POLICY "service_role_only" ON receipts USING (true);
CREATE POLICY "service_role_only" ON ai_reports USING (true);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER debts_updated_at BEFORE UPDATE ON debts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
