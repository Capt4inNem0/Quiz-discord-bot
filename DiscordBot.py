from random import randint

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from games.QuizGame import QuizGame
from games.GuessPhraseGame import GuessPhraseGame


class Bot(commands.Bot):

    def __init__(self, command_prefix, intents=discord.Intents.all(), **options):
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.setup()
        self.settings = {}

    def setup(self):

        @self.command()
        @has_permissions(administrator=True)
        async def guess(ctx):
            game = GuessPhraseGame(self)
            await game.start(ctx)

        @self.command()
        @has_permissions(administrator=True)
        async def quiz(ctx):
            game = QuizGame(self)
            await game.start(ctx)

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)
