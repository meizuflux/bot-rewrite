from asyncpg import Connection, Pool, Record


class CustomPool(Pool):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.cache = {}

    async def register_user(self, game: str, snowflake: int, _id: int):
        query = """
            INSERT INTO
                games (game, snowflake, id)
            VALUES
                ($1, $2, $3)
            ON CONFLICT (games.game, id)
                DO UPDATE
                    SET
                        id = $3
                    WHERE
                        games.game = $1 AND snowflake = $2
            """
        await self.execute(query, game, snowflake, _id)


def create_pool(
    bot,
    dsn=None,
    *,
    min_size=10,
    max_size=10,
    max_queries=50000,
    max_inactive_connection_lifetime=300.0,
    setup=None,
    init=None,
    loop=None,
    connection_class=Connection,
    record_class=Record,
    **connect_kwargs,
) -> CustomPool:
    return CustomPool(
        bot,
        dsn,
        connection_class=connection_class,
        record_class=record_class,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        loop=loop,
        setup=setup,
        init=init,
        max_inactive_connection_lifetime=max_inactive_connection_lifetime,
        **connect_kwargs,
    )
