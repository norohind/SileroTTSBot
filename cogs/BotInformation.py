# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import datetime
import time


class BotInformation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.start_time: float = time.time()
        self.presence_task.start()

    @commands.command('info')
    async def get_info(self, ctx: Context):
        info = f"""
Text-To-Speech bot, based on Silero TTS model (<https://github.com/snakers4/silero-models>)
License: `GNU GENERAL PUBLIC LICENSE Version 3`
Author discord: `a31#6403`
Author email: `a31@demb.design`
Source code on github: <https://github.com/norohind/SileroTTSBot>
Source code on gitea a31's instance: <https://gitea.demb.design/a31/SileroTTSBot>
Invite link: https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot%20applications.commands 
        """

        await ctx.send(info)

    @commands.command('uptime')
    async def uptime(self, ctx: Context):
        uptime = time.time() - self.start_time
        uptime_str = datetime.timedelta(seconds=int(uptime))
        await ctx.send(f"Application is up for {str(uptime_str)}")

    @tasks.loop(seconds=120)
    async def presence_task(self) -> None:
        presence = discord.Game(f"{len(self.bot.guilds)} guilds | @{self.bot.user.name} help")
        await self.bot.change_presence(activity=presence)

    @presence_task.before_loop
    async def presence_task_wait_ready(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(BotInformation(bot))
