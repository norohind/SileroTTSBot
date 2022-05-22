# -*- coding: utf-8 -*-
from formatting import format_table
from discord.ext import commands
from discord.ext.commands import Context


class BotManagement(commands.Cog):
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


async def setup(bot):
    await bot.add_cog(BotManagement(bot))
