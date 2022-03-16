from loguru import logger
from discord.ext import commands
from discord.ext.commands import Context


class cogErrorHandlers:
    @classmethod
    async def missing_argument_handler(cls, ctx: Context, error: Exception) -> None:
        if isinstance(error, commands.errors.MissingRequiredArgument):
            # No argument was specified
            await ctx.reply(str(error))

        else:
            logger.exception(f'Command error occurred: ', exc_info=error)
            await ctx.reply(f'Internal error occurred')
