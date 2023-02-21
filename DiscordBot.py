import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure, has_permissions


class Bot(commands.Bot):

    def __init__(self, command_prefix, intents=discord.Intents.all(), **options):
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.setup()

    def setup(self):

        @self.command(pass_context=True)
        @has_permissions(administrator=True)
        async def whoami(ctx):
            msg = "You're an admin {}".format(ctx.message.author.mention)
            await ctx.send(msg)

        @whoami.error
        async def whoami_error(ctx, error):
            if isinstance(error, CheckFailure):
                msg = "You're an average joe {}".format(ctx.message.author.mention)
                await ctx.send(msg)

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)
