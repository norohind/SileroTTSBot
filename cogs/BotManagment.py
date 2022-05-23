# -*- coding: utf-8 -*-
from formatting import format_table
from discord.ext import commands
from discord.ext.commands import Context
import rfoo
from rfoo.utils import rconsole
from threading import Thread
from typing import Optional
from loguru import logger


class BotManagement(commands.Cog):
    rfoo_server_thread: Optional[Thread] = None
    rfoo_server: Optional[rfoo.InetServer] = None

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

    @commands.is_owner()
    @commands.command('rfooStart')
    async def start(self, ctx: Context):
        if self.rfoo_server_thread is None:
            self.rfoo_server = rfoo.InetServer(rconsole.ConsoleHandler, {'bot': self.bot})
            self.rfoo_server_thread = Thread(target=lambda: self.rfoo_server.start(rfoo.LOOPBACK, 54321))
            self.rfoo_server_thread.daemon = True
            self.rfoo_server_thread.start()
            logger.info('Rfoo thread started by msg')
            await ctx.send('Rfoo thread started')

        else:
            await ctx.send('Rfoo thread already started')

    @commands.is_owner()
    @commands.command('rfooStop')
    async def stop(self, ctx: Context):
        if self.rfoo_server_thread is not None:
            self.rfoo_server.stop()
            del self.rfoo_server_thread
            logger.info('Rfoo thread stopped by msg')
            await ctx.send('Rfoo server stopped')

        else:
            await ctx.send('Rfoo server already stopped')


async def setup(bot):
    await bot.add_cog(BotManagement(bot))
