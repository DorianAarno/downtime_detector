import asyncio
import os
import sys
import time
import traceback

import aiomysql
from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel
from disnake import Color, Intents
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

class MyBot(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brand_color = Color.blurple()
        self.logger = None

    async def setup(self):
        # create logger without default handlers
        logger = Logger(name="Bot-logs", level=LogLevel.DEBUG)

        # AsyncStreamHandler and Formatter from aiologger
        handler = AsyncStreamHandler(stream=sys.stdout)
        formatter = Formatter(
            fmt="%(asctime)s UTC - %(name)s - %(levelname)s: %(message)s"
        )
        # Set the Formatter to use UTC time
        formatter.converter = time.gmtime
        handler.formatter = formatter

        # Add the custom handler to logger
        logger.add_handler(handler)
        self.logger = logger

    async def create_pool(self):
        self.db_pool = await aiomysql.create_pool(
            host=os.getenv("RDS_HOST"),
            port=int(os.getenv("RDS_PORT")),
            user=os.getenv("RDS_USERNAME"),
            password=os.getenv("RDS_PASSWORD"),
            db=os.getenv("RDS_DATABASE"),
            autocommit=True,
            loop=self.loop,
        )

    async def execute(self, query, *values):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple(values))
            await conn.commit()

    async def executemany(self, query, values_list):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, values_list)
            await conn.commit()

    async def fetchrow(self, query, *values):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple(values))
                row = await cur.fetchone()
            if row:
                row = [r for r in row]
            else:
                row = None
            return row

    async def fetchval(self, query, *values):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple(values))
                row = await cur.fetchone()
            if row:
                item = row[0]
            else:
                item = None
            return item

    async def fetch(self, query, *values):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple(values))
                all = await cur.fetchall()
            return all

    def get_slash_id(self, name):
        cmd_id = 0
        for app in self.global_slash_commands:
            if app.name == name:
                cmd_id = app.id
                break

        return cmd_id

    async def setup_tables(self):
        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS monitored_bots(
                guild_id BIGINT,
                bot_user_id BIGINT,
                alert_type INTEGER,
                alert_entity_id BIGINT,
                current_status INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ) 
        # alert type 0 = reminder channel
        # alert type 1 = dms
        


def setup_bot(bot):
    try:

        @bot.before_slash_command_invoke
        async def before_invoke_slash(inter):
            if not inter.response.is_done():
                await inter.response.defer()

        # Load all cogs
        for filename in os.listdir("cogs"):
            if filename.endswith(".py"):
                bot.load_extension(f"cogs.{filename[:-3]}")
    except Exception as e:
        raise e


async def main():
    intents = Intents.default()
    intents.presences = True
    intents.members = True

    bot = MyBot(intents=intents)
    await bot.setup()
    await bot.create_pool()
    await bot.setup_tables()
    setup_bot(bot)

    try:

        async def inform_ready_up():
            await bot.wait_until_ready()
            if not os.path.exists("tmp"):
                os.makedirs("tmp")
            await bot.logger.info("*********\nBot is Ready.\n*********")

        bot.loop.create_task(inform_ready_up())
        await bot.start(TOKEN)

    except Exception as e:
        await bot.logger.error(traceback.format_exc())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
