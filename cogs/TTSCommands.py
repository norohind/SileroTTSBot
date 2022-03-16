# -*- coding: utf-8 -*-
import subprocess

from discord.ext import commands
from discord.ext.commands import Context
import discord
import DB
from typing import Union
from loguru import logger
from TTSSilero import TTSSileroCached
from TTSSilero import Speakers
from FFmpegPCMAudioModified import FFmpegPCMAudio
import Observ
from cogErrorHandlers import cogErrorHandlers


class TTSCommands(commands.Cog, Observ.Observer):
    DEFAULT_SPEAKER = Speakers.kseniya

    def __init__(self, bot: Union[commands.Bot, Observ.Subject]):
        self.bot = bot
        self.cog_command_error = cogErrorHandlers.missing_argument_handler
        self.bot.subscribe(self)  # subscribe for messages that aren't commands
        self.tts = TTSSileroCached()

    @commands.command('exit')
    async def leave_voice(self, ctx: Context):
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.disconnect(force=False)
            await ctx.channel.send(f"Left voice channel")
            return

        else:
            await ctx.channel.send("I'm not in any voice channel")
            return

    async def update(self, message: discord.Message):
        """
        Like on_message but only for messages which aren't commands

        :param message:
        :return:
        """

        if message.author == self.bot.user:
            return

        if message.author.bot:
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        logger.info(f'Message: {message.content}')
        user_voice_state = message.author.voice
        if user_voice_state is None:
            await message.channel.send(f"You're not in a voice channel")
            return

        # noinspection PyTypeChecker
        voice_client: discord.VoiceClient = message.guild.voice_client
        if voice_client is None:
            voice_client: discord.VoiceClient = await user_voice_state.channel.connect()

        speaker: Speakers = await self._get_speaker(message.guild.id)

        # check if message will fail on synthesis
        if DB.SynthesisErrors.select()\
                .where(DB.SynthesisErrors.speaker == speaker.value)\
                .where(DB.SynthesisErrors.text == message.content)\
                .count() == 1:
            # Then we will not try to synthesis it
            await message.channel.send(f"I will not synthesis this message due to TTS engine limitations")
            return

        try:
            wav_file_like_object = self.tts.synthesize_text(message.content, speaker=speaker)
            sound_source = FFmpegPCMAudio(wav_file_like_object, pipe=True, stderr=subprocess.PIPE)
            voice_client.play(sound_source)

        except Exception as synth_exception:
            logger.opt(exception=True).warning(f'Exception on synthesize {message.content!r}: {synth_exception}')
            await message.channel.send(f'Internal error')
            DB.SynthesisErrors.create(speaker=speaker.value, text=message.content)

    @commands.command('getAllSpeakers')
    async def get_speakers(self, ctx: Context):
        speakers = '\n'.join([speaker.name for speaker in Speakers])

        await ctx.send(f"```\n{speakers}```")

    @commands.command('setSpeaker')
    async def set_speaker(self, ctx: Context, speaker: str):
        try:
            checked_speaker: Speakers = Speakers(speaker)
            DB.Speaker.replace(server_id=ctx.guild.id, speaker=checked_speaker.value).execute()
            await ctx.send(f'Successfully set speaker to `{checked_speaker.value}`')

        except KeyError:
            await ctx.send(f"Provided speaker is invalid, provided speaker must be from `getAllSpeakers` command")

    @commands.command('getSpeaker')
    async def get_speaker(self, ctx: Context):
        speaker = await self._get_speaker(ctx.guild.id)

        await ctx.send(f'Your current speaker is `{speaker.value}`')

    async def _get_speaker(self, guild_id: int) -> Speakers:
        try:
            speaker = Speakers(DB.Speaker[guild_id].speaker)

        except DB.peewee.DoesNotExist:
            speaker = self.DEFAULT_SPEAKER

        return speaker


async def setup(bot):
    await bot.add_cog(TTSCommands(bot))
