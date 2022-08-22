# -*- coding: utf-8 -*-
import asyncio
import time
from formatting import format_table
from discord.ext import commands
from discord.ext.commands import Context
import rfoo
from rfoo.utils import rconsole
from threading import Thread
from typing import Optional, Coroutine
from loguru import logger


class SingletonBase:
    def __new__(cls, *args, **kwargs):
        if getattr(cls, 'instance') is None:
            cls.instance = super().__new__(cls, *args, **kwargs)

        # logger.debug(id(getattr(cls, 'instance')))
        return getattr(cls, 'instance')


class BotManagement(commands.Cog, SingletonBase):
    instance: Optional['BotManagement'] = None

    rfoo_server_thread: Optional[Thread] = None
    rfoo_server: Optional[rfoo.InetServer] = None

    # def __new__(cls, *args, **kwargs):
    #     if cls.instance is None:
    #         cls.instance = super().__new__(cls, *args, **kwargs)
    #
    #     return cls.instance

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command('listServers')
    async def list_servers(self, ctx: Context):
        text_table = format_table(((server.name, str(server.id)) for server in self.bot.guilds), ('name', 'id'))
        await ctx.channel.send(text_table)

    @commands.is_owner()
    @commands.command('listVoice')
    async def list_voice_connections(self, ctx: Context):
        text_table = format_table(((it.guild.name,) for it in self.bot.voice_clients))
        await ctx.channel.send(text_table)

    def start_rfoo(self) -> bool:
        # True if started, False if already started
        if self.rfoo_server_thread is None:
            self.rfoo_server = rfoo.InetServer(rconsole.ConsoleHandler, {'bot': self.bot, 'ct': self.ct})
            self.rfoo_server_thread = Thread(target=lambda: self.rfoo_server.start(rfoo.LOOPBACK, 54321))
            self.rfoo_server_thread.daemon = True
            self.rfoo_server_thread.start()
            logger.info('Rfoo thread started by msg')
            return True

        return False

    def stop_rfoo(self) -> bool:
        if self.rfoo_server_thread is not None:
            self.rfoo_server.stop()
            del self.rfoo_server_thread
            logger.info('Rfoo thread stopped by msg')
            return True

        return False

    @commands.is_owner()
    @commands.command('rfooStart')
    async def start(self, ctx: Context):
        if self.start_rfoo():
            await ctx.send('Rfoo thread started')

        else:
            await ctx.send('Rfoo thread already started')

    @commands.is_owner()
    @commands.command('rfooStop')
    async def stop(self, ctx: Context):
        if self.stop_rfoo():
            await ctx.send('Rfoo server stopped')

        else:
            await ctx.send('Rfoo server already stopped')

    def ct(self, coro: Coroutine):
        """
        ct - short from create_task
        execute coroutine and get result
        """

        task = self.bot.loop.create_task(coro)
        while not task.done():
            time.sleep(0.1)

        try:
            return task.result()

        except asyncio.exceptions.InvalidStateError:
            return task.exception()


async def setup(bot: commands.Bot):
    await bot.add_cog(BotManagement(bot))


async def teardown(bot):
    stop_res = BotManagement(bot).stop_rfoo()
    logger.info(f'Unloaded rfoo with result {stop_res} during BotManagement unload')
