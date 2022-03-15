import time
from typing import Union

from .TTSSilero import TTSSilero
from .Speakers import Speakers
import DB
import sqlite3
from loguru import logger


class TTSSileroCached(TTSSilero):
    _SQLITE_GET = "select audio from soundcache where text = :text and speaker = :speaker;"
    _SQLITE_SET = "insert into soundcache (text, speaker, audio) values (:text, :speaker, :audio);"
    _SQLITE_INCREMENT_USAGES = "update soundcache set usages = usages + 1 where text = :text and :speaker = :speaker;"
    _SQLITE_SCHEMA = """CREATE TABLE IF NOT EXISTS "soundcache" (
    "text" TEXT NOT NULL, 
    "speaker" VARCHAR(255) NOT NULL, 
    "audio" BLOB NOT NULL, 
    "usages" INTEGER NOT NULL default 0, 
    PRIMARY KEY ("text", "speaker")
    );"""

    database: sqlite3.Connection = DB.database.connection()

    def __init__(self):
        super().__init__()
        self.database.execute(self._SQLITE_SCHEMA)

    def synthesize_text(self, text: str, speaker: Speakers = Speakers.kseniya) -> bytes:
        # start = time.time()
        cached = self._cache_get(text, speaker.value)
        # logger.debug(f'Cache lookup in {time.time() - start} s')
        if cached is not None:
            # logger.debug(f'Cache lookup successful in {time.time() - start} s')
            return cached

        else:
            # logger.debug(f'Starting synthesis')
            # start2 = time.time()
            synthesized = super().synthesize_text(text, speaker)
            # logger.debug(f'Synthesis done in {time.time() - start2} s in {time.time() - start} s after start')
            self._cache_set(text, speaker.value, synthesized)
            # logger.debug(f'Cache set in {time.time() - start2} synth end and {time.time() - start2} s after start')
            return synthesized

    def _cache_get(self, text: str, speaker: str) -> Union[bytes, None]:
        query_args = {'text': text, 'speaker': speaker}
        result = self.database.execute(self._SQLITE_GET, query_args).fetchone()
        if result is None:
            return None

        else:
            with self.database:
                self.database.execute(self._SQLITE_INCREMENT_USAGES, query_args)

            return result[0]

    def _cache_set(self, text: str, speaker: str, audio: bytes) -> None:
        with self.database:
            self.database.execute(self._SQLITE_SET, {'text': text, 'speaker': speaker, 'audio': audio})
