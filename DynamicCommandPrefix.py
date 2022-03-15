# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import peewee
import DB
# from loguru import logger


def dynamic_command_prefix(bot: commands.Bot, message: discord.Message) -> list[str]:
    mention_prefixes = commands.bot.when_mentioned(bot, message)

    custom_prefix = get_guild_prefix(message.guild.id)
    all_prefixes = mention_prefixes + [custom_prefix + ' ', custom_prefix]

    # logger.debug(f'Return prefixes {all_prefixes!r} for {message.content!r}')
    return all_prefixes


def get_guild_prefix(guild_id: int) -> str:
    try:
        prefix = DB.Prefix[guild_id].prefix_char

    except peewee.DoesNotExist:
        prefix = 'tts '

    return prefix
