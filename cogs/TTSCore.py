# -*- coding: utf-8 -*-
import subprocess
import time
from collections import defaultdict
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
from SpeakersSettingsAdapterDiscord import speakers_settings_adapter, SpeakersSettingsAdapterDiscord


class TTSCore(commands.Cog, Observ.Observer):
    def __init__(self, bot: Union[commands.Bot, Observ.Subject]):
        self.bot = bot
        self.cog_command_error = cogErrorHandlers.missing_argument_handler
        self.bot.subscribe(self)  # subscribe for messages that aren't commands
        self.tts = TTSSileroCached()
        self.tts_queues: dict[int, list[discord.AudioSource]] = defaultdict(list)
        self.speakers_adapter: SpeakersSettingsAdapterDiscord = speakers_settings_adapter

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

        logger.info(f'Message to say: {message.content}')
        user_voice_state = message.author.voice
        if user_voice_state is None:
            await message.channel.send(f"You're not in a voice channel")
            return

        # noinspection PyTypeChecker
        voice_client: discord.VoiceClient = message.guild.voice_client
        if voice_client is None:
            voice_client: discord.VoiceClient = await user_voice_state.channel.connect()

        speaker: Speakers = self.speakers_adapter.get_speaker(message.guild.id, message.author.id)

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
            if voice_client.is_playing():
                # Then we need to enqueue prepared sound for playing through self.tts_queues mechanism

                self.tts_queues[message.guild.id].append(sound_source)
                await message.channel.send(f"Enqueued for play, queue size: {len(self.tts_queues[message.guild.id])}")
                return

            voice_client.play(sound_source, after=lambda e: self.queue_player(message))

        except Exception as synth_exception:
            logger.opt(exception=True).warning(f'Exception on synthesize {message.content!r}: {synth_exception}')
            await message.channel.send(f'Internal error')
            DB.SynthesisErrors.create(speaker=speaker.value, text=message.content)

    def queue_player(self, message: discord.Message):
        voice_client: Union[discord.VoiceClient, None] = message.guild.voice_client
        if voice_client is None:
            # don't play anything and clear queue for whole guild
            del self.tts_queues[message.guild.id]
            return

        for sound_source in self.tts_queues[message.guild.id]:
            voice_client.play(sound_source)
            while voice_client.is_playing():
                time.sleep(0.1)

        try:
            del self.tts_queues[message.guild.id]

        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is None:
            members = before.channel.members
            if len(members) == 1:
                if members[0].id == self.bot.user.id:
                    await before.channel.guild.voice_client.disconnect(force=False)


async def setup(bot):
    await bot.add_cog(TTSCore(bot))
