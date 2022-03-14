import io
import sqlite3


class Cache:
    SCHEMA = "create table if not exists cache (key text primary key, value blob);"
    SET = "insert into cache (key, value) values (:key, :value);"
    GET = "select value from cache where key = :key;"

    def __init__(self):
        self.connection = sqlite3.connect('voice_cache.sqlite')
        self.connection.execute(self.SCHEMA)

    def set(self, key: str, value: bytes) -> None:
        with self.connection:
            self.connection.execute(self.SET, {'key': key, 'value': value})

    def get(self, key: str):
        res = self.connection.execute(self.GET, {'key': key}).fetchone()
        if res is None:
            return None

        else:
            return io.BytesIO(res[0])


cache = Cache()
