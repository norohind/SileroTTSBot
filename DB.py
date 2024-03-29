import os
from datetime import datetime
from pathlib import Path

import peewee

DB_PATH = Path(os.getenv('DATA_DIR', '.')) / 'voice_cache.sqlite'
database = peewee.SqliteDatabase(str(DB_PATH))


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Prefix(BaseModel):
    server_id = peewee.BigIntegerField(primary_key=True)
    prefix_char = peewee.CharField(max_length=10)


class ServerSpeaker(BaseModel):
    server_id = peewee.BigIntegerField(primary_key=True)
    speaker = peewee.CharField()


class UserServerSpeaker(peewee.Model):
    """
    Holds the data about custom speakers for users in per server way
    """

    server_id = peewee.BigIntegerField()
    user_id = peewee.BigIntegerField()
    speaker = peewee.CharField()

    class Meta:
        database = database
        primary_key = peewee.CompositeKey('server_id', 'user_id')


class SynthesisErrors(peewee.Model):
    speaker = peewee.CharField()
    text = peewee.TextField()
    timestamp = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = database
        primary_key = peewee.CompositeKey('speaker', 'text')


class SoundCache(peewee.Model):
    text = peewee.TextField()
    speaker = peewee.CharField()
    audio = peewee.BlobField()
    usages = peewee.IntegerField(default=1)

    class Meta:
        database = database
        primary_key = peewee.CompositeKey('speaker', 'text')


Prefix.create_table()
ServerSpeaker.create_table()
SynthesisErrors.create_table()
SoundCache.create_table()
UserServerSpeaker.create_table()
