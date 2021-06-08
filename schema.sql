CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS prefixes (
    id BIGINT PRIMARY KEY REFERENCES guilds (id) ON DELETE CASCADE,
    prefix VARCHAR(25)
);

CREATE TABLE IF NOT EXISTS games (
    game TEXT,
    snowflake BIGINT,
    id VARCHAR,
    PRIMARY KEY (game, snowflake)
);

CREATE TABLE IF NOT EXISTS interactions (
    method TEXT,
    initiator BIGINT,
    receiver BIGINT,
    count BIGINT DEFAULT 1,
    PRIMARY KEY (method, initiator, receiver)
);

CREATE TABLE IF NOT EXISTS totals (
    method TEXT,
    snowflake BIGINT,
    count BIGINT DEFAULT 1,
    PRIMARY KEY (method, snowflake)
)