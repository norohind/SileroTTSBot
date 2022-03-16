# -*- coding: utf-8 -*-
from discord.ext import commands
from discord.ext.commands import Context
from TTSSilero import Speakers
from cogErrorHandlers import cogErrorHandlers
from SpeakersSettingsAdapterDiscord import speakers_settings_adapter, SpeakersSettingsAdapterDiscord


class TTSSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_command_error = cogErrorHandlers.missing_argument_handler
        self.speakers_adapter: SpeakersSettingsAdapterDiscord = speakers_settings_adapter

    @commands.command('getAllSpeakers')
    async def get_speakers(self, ctx: Context):
        """
        Enumerate all available to set speakers

        :param ctx:
        :return:
        """
        speakers = '\n'.join(self.speakers_adapter.available_speakers)

        await ctx.send(f"```\n{speakers}```")

    @commands.command('setPersonalSpeaker')
    async def set_user_speaker(self, ctx: Context, speaker: str):
        """
        Set personal speaker on this server

        :param ctx:
        :param speaker:
        :return:
        """
        try:
            checked_speaker: Speakers = Speakers(speaker)
            self.speakers_adapter.set_speaker_user(ctx.guild.id, ctx.author.id, checked_speaker)
            await ctx.reply(f'Successfully set **your personal** speaker to `{checked_speaker.value}`')

        except (KeyError, ValueError):
            await ctx.send(f"Provided speaker is invalid, provided speaker must be from `getAllSpeakers` command")

    @commands.command('setServerSpeaker')
    async def set_server_speaker(self, ctx: Context, speaker: str):
        """
        Set global server speaker

        :param ctx:
        :param speaker:
        :return:
        """
        try:
            checked_speaker: Speakers = Speakers(speaker)
            self.speakers_adapter.set_speaker_global(ctx.guild.id, checked_speaker)
            await ctx.send(f'Successfully set **server** speaker to `{checked_speaker.value}`')

        except (KeyError, ValueError):
            await ctx.send(f"Provided speaker is invalid, provided speaker must be from `getAllSpeakers` command")

    @commands.command('getSpeaker')
    async def get_speaker(self, ctx: Context):
        """
        Tell first appropriate speaker for a user, it can be user specified, server specified or server default

        :param ctx:
        :return:
        """
        speaker = self.speakers_adapter.get_speaker(ctx.guild.id, ctx.author.id)

        await ctx.reply(f'Your current speaker is `{speaker.value}`')

    @commands.command('getPersonalSpeaker')
    async def get_personal_speaker(self, ctx: Context):
        """
        Tell user his personal speaker on this server, if user don't have personal speaker, tells server default one

        :param ctx:
        :return:
        """
        speaker = self.speakers_adapter.get_speaker_user(ctx.guild.id, ctx.author.id)
        if speaker is None:
            server_speaker = self.speakers_adapter.get_speaker_global(ctx.guild.id).value
            await ctx.send(f"You currently don't have a personal speaker, current server speaker is `{server_speaker}`")

        else:
            await ctx.reply(f"Your personal speaker is `{speaker.value}`")

    @commands.command('getServerSpeaker')
    async def get_server_speaker(self, ctx: Context):
        """
        Tell server global speaker

        :param ctx:
        :return:
        """
        speaker = self.speakers_adapter.get_speaker_global(ctx.guild.id)
        await ctx.send(f"Current server speaker is `{speaker.value}`")


async def setup(bot):
    await bot.add_cog(TTSSettings(bot))
