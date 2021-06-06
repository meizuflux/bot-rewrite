CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT PRIMARY KEY
),

CREATE TABLE IF NOT EXISTS games (
    game TEXT,
    snowflake BIGINT,
    id BIGINT,
    PRIMARY KEY (game, id)
)