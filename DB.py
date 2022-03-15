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


Prefix.create_table()
Speaker.create_table()
