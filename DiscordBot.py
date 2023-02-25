import asyncio
from threading import Thread

import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure, has_permissions
import time as tm


class Bot(commands.Bot):

    def __init__(self, command_prefix, intents=discord.Intents.all(), **options):
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.setup()
        self.settings = {}
        self.responses = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

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

        @self.command(pass_context=True)
        @has_permissions(administrator=True)
        async def select(ctx):
            msg = "Setting this channel for quiz game."
            await ctx.send(msg)
            if ctx.guild.id not in self.settings:
                self.settings[ctx.guild.id] = {}
            self.settings[ctx.guild.id]['channel'] = ctx.channel.id

        @self.command(pass_context=True)
        @has_permissions(administrator=True)
        async def getsettings(ctx):
            msg = "Settings: {}".format(self.settings)
            await ctx.send(msg)

        @self.command(pass_context=True)
        @has_permissions(administrator=True)
        async def startgame(ctx):
            msg = "Starting game..."
            await ctx.send(msg)
            if ctx.guild.id not in self.settings:
                msg = "No settings found for this server."
                await ctx.send(msg)
                return
            if 'channel' not in self.settings[ctx.guild.id]:
                msg = "No game channel selected for this server. Use ?select to select a channel."
                await ctx.send(msg)
                return
            channel = self.get_channel(self.settings[ctx.guild.id]['channel'])
            await channel.send("Game started!")

        @self.command()
        async def quiz(ctx):
            await self.ask(ctx, "What is the capital of France?", ["Paris", "London", "Berlin", "Rome"], 0)

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)

    async def ask(self, ctx, question, answers, correct_answer=0, max_winners=3):
        assert len(answers) == 4, "There must be 4 answers"
        msg = f"""
        {question}
        1. {answers[0]}
        2. {answers[1]}
        3. {answers[2]}
        4. {answers[3]}
        """
        msg = await ctx.send(msg)  # Message to react to
        for response in self.responses:
            asyncio.get_event_loop().create_task(msg.add_reaction(response))

        results = await self.check_responses(msg, correct_answer)  # Wait for a reaction
        positions_string = ""
        position = 1
        for user, time in results.items():
            positions_string += f"{position}. {user.mention} - {time:.2f} seconds\n"
            if position == max_winners:
                break
            position += 1
        await ctx.send(positions_string)

    async def check_responses(self, message, correct_answer=0, time_limit=10):
        def check(reaction, user):
            return str(reaction.emoji) == self.responses[correct_answer] and user != self.user
        reactions_user_time = {}  # Dictionary to store the reactions and the time the user reacted
        start_time = tm.time()
        timeout = False
        while not timeout:
            try:
                reaction = await self.wait_for("reaction_add", timeout=0.5, check=check)  # Wait for a reaction
                reactions_user_time[reaction[1]] = tm.time() - start_time
            except asyncio.TimeoutError:
                pass
            timeout = (tm.time() - start_time) > time_limit  # If the time is more than 10 seconds
        await message.channel.send("Time is up!")
        results = dict(sorted(reactions_user_time.items(), key=lambda item: item[1]))
        return results  # Display the dictionary

