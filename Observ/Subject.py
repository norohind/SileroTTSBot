import discord
from .Observer import Observer


class Subject:
    observers: set = set()

    def subscribe(self, observer: Observer) -> None:
        self.observers.add(observer)

    def unsubscribe(self, observer: Observer) -> None:
        try:
            self.observers.remove(observer)

        except KeyError:
            pass

    async def notify(self, message: discord.Message) -> None:
        for observer in self.observers:
            await observer.update(message)
