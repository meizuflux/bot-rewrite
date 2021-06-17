CREATE SCHEMA IF NOT EXISTS events;

CREATE TABLE IF NOT EXISTS events.reminders (
    id SERIAL PRIMARY KEY,

    guild BIGINT REFERENCES guilds (id) ON DELETE CASCADE,
    author BIGINT,
    channel BIGINT,
    message BIGINT,

    expires TIMESTAMP,
    created TIMESTAMP,

    content TEXT
);

CREATE TABLE IF NOT EXISTS events.timers (
    id SERIAL PRIMARY KEY,

    event TEXT NOT NULL,
    created TIMESTAMPTZ NOT NULL,
    expires TIMESTAMPTZ NOT NULL,
    data JSONB NOT NULL
)