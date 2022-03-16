# -*- coding: utf-8 -*-

from discord.ext import commands
from discord.ext.commands import Context
import datetime
import time


class BotInformation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.start_time: float = time.time()

    @commands.command('info')
    async def get_info(self, ctx: Context):
        info = f"""
Text-To-Speech bot, based on Silero TTS model (<https://github.com/snakers4/silero-models>)
License: `GNU GENERAL PUBLIC LICENSE Version 3`
Author discord: `a31#6403`
Author email: `a31@demb.design`
Source code on github: <https://github.com/norohind/SileroTTSBot>
Source code on gitea's a31 instance: <https://gitea.demb.design/a31/SileroTTSBot>
Invite link: https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot%20applications.commands 
        """

        await ctx.send(info)

    @commands.command('uptime')
    async def uptime(self, ctx: Context):
        uptime = time.time() - self.start_time
        uptime_str = datetime.timedelta(seconds=int(uptime))
        await ctx.send(f"Application is up for {str(uptime_str)}")


async def setup(bot):
    await bot.add_cog(BotInformation(bot))
