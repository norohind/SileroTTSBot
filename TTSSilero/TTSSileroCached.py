import time
from typing import Union

from .TTSSilero import TTSSilero
from .Speakers import Speakers
import DB
import sqlite3
from loguru import logger


class TTSSileroCached(TTSSilero):
    def synthesize_text(self, text: str, speaker: Speakers = Speakers.kseniya) -> bytes:
        # start = time.time()
        cache_query = DB.SoundCache.select()\
            .where(DB.SoundCache.text == text)\
            .where(DB.SoundCache.speaker == speaker.value)

        if cache_query.count() == 1:
            with DB.database.atomic():
                DB.SoundCache.update({DB.SoundCache.usages: DB.SoundCache.usages + 1})\
                    .where(DB.SoundCache.text == text)\
                    .where(DB.SoundCache.speaker == speaker.value).execute()

                cached = cache_query.get().audio

            return cached

        else:
            # logger.debug(f'Starting synthesis')
            # start2 = time.time()
            synthesized = super().synthesize_text(text, speaker)
            # logger.debug(f'Synthesis done in {time.time() - start2} s in {time.time() - start} s after start')
            DB.SoundCache.create(text=text, speaker=speaker.value, audio=synthesized)

            # logger.debug(f'Cache set in {time.time() - start2} synth end and {time.time() - start2} s after start')
            return synthesized
