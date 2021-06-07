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
    id BIGINT,
    PRIMARY KEY (game, snowflake)
)