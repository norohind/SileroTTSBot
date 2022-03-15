# -*- coding: utf-8 -*-
from discord.ext import commands
from discord.ext.commands import Context
import DB
from loguru import logger
import DynamicCommandPrefix
from cogErrorHandlers import cogErrorHandlers


class prefixConfiguration(commands.Cog):
    """
    Cog for manage prefix in per server way
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_command_error = cogErrorHandlers.missing_argument_handler

    @commands.command('setPrefix')
    async def set_prefix(self, ctx: Context, prefix: str):
        logger.debug(f'Going to set prefix')
        if len(prefix) > DB.Prefix.prefix_char.max_length:
            await ctx.reply(f'Prefix must be one symbol')
            return

        DB.Prefix.replace(server_id=ctx.guild.id, prefix_char=prefix).execute()

        logger.debug(f'Set prefix {prefix!r} for guild {ctx.guild.name!r}')
        await ctx.reply(f'Your new prefix is `{prefix}`')

    @commands.command('getPrefix')
    async def get_prefix(self, ctx: Context):
        prefix = DynamicCommandPrefix.get_guild_prefix(ctx.guild.id)
        await ctx.reply(f'Your current prefix is `{prefix}` and <@{self.bot.user.id}>')

    @commands.command('resetPrefix')
    async def reset_prefix(self, ctx: Context):
        DB.Prefix.delete().where(DB.Prefix.server_id == ctx.guild.id).execute()
        await ctx.reply(f'Your prefix was deleted')


async def setup(bot):
    await bot.add_cog(prefixConfiguration(bot))
