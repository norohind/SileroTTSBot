# -*- coding: utf-8 -*-
import os
import time

import discord
import signal
import asyncio
from loguru import logger

import utils
from TTSSilero import TTS
from TTSSilero import Speakers
from FFmpegPCMAudioModified import FFmpegPCMAudio
from Cache import cache

tts = TTS()
"""
while msg := input('$ '):
    start = time.time()
    audio = tts.synthesize_text(msg, speaker=Speakers.kseniya)
    print('synthesize took ', str(time.time() - start))
    utils.play_bytes_io(audio)
"""


class DiscordTTSBot(discord.Client):
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

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if not message.content.startswith('-'):
            return

        if isinstance(message.channel, discord.TextChannel):
            logger.info(f'Message: {message.content}')
            user_voice_state = message.author.voice
            if message.content.startswith('/exit'):
                if message.guild.voice_client is not None:
                    logger.debug(f'Disconnecting from voice channel')
                    await message.guild.voice_client.disconnect(force=False)
                    await message.channel.send(f"Left voice channel")
                    return

                else:
                    await message.channel.send("I'm not in any voice channel")
                    return

            if user_voice_state is None:
                await message.channel.send(f"You're not in a voice channel")
                return

            # noinspection PyTypeChecker
            voice_client: discord.VoiceClient = message.guild.voice_client
            if voice_client is None:
                voice_client: discord.VoiceClient = await user_voice_state.channel.connect()

            cached = cache.get(message.content)
            if cached is not None:
                wav_file_like_object = cached
                logger.debug(f'Cache lookup for {message.content!r} successful')

            else:
                synthesis_start = time.time()
                wav_file_like_object = tts.synthesize_text(message.content, seek=0)
                logger.debug(f'Synthesis took {time.time() - synthesis_start} s')
                cache.set(message.content, wav_file_like_object.read())
                logger.debug(f'Set cache for {message.content!r}')
                wav_file_like_object.seek(0)

            sound_source = FFmpegPCMAudio(
                wav_file_like_object.read(),
                pipe=True
            )
            voice_client.play(sound_source, after=lambda e: logger.debug(f"Player done, {e=}"))


intents = discord.Intents.default()
intents.message_content = True

discord_client = DiscordTTSBot(intents=intents)

loop = asyncio.new_event_loop()
loop.run_until_complete(discord_client.start(os.environ['DISCORD_TOKEN']))
logger.debug('Shutdown completed')
