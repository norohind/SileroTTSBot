# -*- coding: utf-8 -*-
import os
from discord.ext import commands
import discord
import signal
import asyncio
from loguru import logger
from DynamicCommandPrefix import dynamic_command_prefix
import Observ


logger.add('offlineTTSBot.log', backtrace=True, diagnose=False, rotation='5MB')

"""
while msg := input('$ '):
    start = time.time()
    audio = tts.synthesize_text(msg, speaker=Speakers.kseniya)
    print('synthesize took ', str(time.time() - start))
    utils.play_bytes_io(audio)
"""


class DiscordTTSBot(commands.Bot, Observ.Subject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        logger.info('Shutdown callbacks registered')

    def shutdown(self, sig, frame):
        logger.info(f'Shutting down by signal: {sig}')
        asyncio.create_task(self.close())

    async def on_ready(self):
        logger.debug('Bot is ready')

    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return

        await super(DiscordTTSBot, self).on_message(message)
        if message.author.bot:  # because on_command_error will not be called if author is bot
            # so it isn't a command, so, pass it next
            await self.notify(message)

    async def on_command_error(self, ctx: commands.Context, exception: commands.errors.CommandError) -> None:
        if isinstance(exception, commands.errors.CommandNotFound):
            ctx.message.content = ctx.message.content[len(ctx.prefix):]  # skip prefix
            await self.notify(ctx.message)

        else:
            raise exception


intents = discord.Intents.default()
intents.message_content = True

discord_client = DiscordTTSBot(command_prefix=dynamic_command_prefix, intents=intents)


async def main():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            logger.debug(f'Loading extension {filename}')
            await discord_client.load_extension(f"cogs.{filename[:-3]}")

    await discord_client.start(os.environ['DISCORD_TOKEN'])

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
logger.debug('Shutdown completed')
