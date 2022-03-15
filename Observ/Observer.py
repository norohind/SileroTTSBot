from abc import ABC, abstractmethod
import discord


class Observer:
    @abstractmethod
    def update(self, message: discord.Message) -> None:
        raise NotImplemented
