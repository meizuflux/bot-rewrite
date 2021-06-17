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