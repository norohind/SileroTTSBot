from datetime import datetime

import peewee

database = peewee.SqliteDatabase('voice_cache.sqlite')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Prefix(BaseModel):
    server_id = peewee.BigIntegerField(primary_key=True)
    prefix_char = peewee.CharField(max_length=10)


class Speaker(BaseModel):
    server_id = peewee.BigIntegerField(primary_key=True)
    speaker = peewee.CharField()


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
Speaker.create_table()
SynthesisErrors.create_table()
SoundCache.create_table()
