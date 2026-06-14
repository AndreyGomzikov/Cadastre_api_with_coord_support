CREATE TABLE IF NOT EXISTS cadastral_requests (
    id BIGSERIAL PRIMARY KEY,
    cadastral_number TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    external_result BOOLEAN NOT NULL,
    external_status_code INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cadastral_requests_number
    ON cadastral_requests (cadastral_number);

CREATE INDEX IF NOT EXISTS idx_cadastral_requests_created_at
    ON cadastral_requests (created_at DESC);
