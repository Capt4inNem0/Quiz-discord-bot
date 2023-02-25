import asyncio
import json
from random import randint

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
        @self.command()
        @has_permissions(administrator=True)
        async def quiz(ctx):
            file = open('qustions.json', mode='r')
            questions = json.load(file)['data']
            file.close()
            min_range = min(len(questions), 20)
            total_points = {}
            for i in range(min_range):
                index = randint(0, len(questions) - 1)
                question = questions[index]
                questions.pop(index)
                results = await self.ask(ctx, question['question'], question['options'], question['correct_answer'])
                for user, time in results.items():
                    if user not in total_points:
                        total_points[user] = 0
                    total_points[user] += 100/time
            await ctx.send("The quiz is over!")
            overall_string = ""
            total_points_sorted = dict(reversed(sorted(total_points.items(), key=lambda item: item[1])))
            max_winners = min(len(total_points_sorted), 20)
            position = 1
            for user, points in total_points_sorted.items():
                if position > max_winners:
                    break
                overall_string += f"{position}. {user.mention} - {points} points\n"
                position += 1
            await ctx.send(overall_string)
            await asyncio.sleep(3)

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
        if len(positions_string) == 0:
            positions_string = "No one got it right!"
        await ctx.send(positions_string)
        return results

    async def check_responses(self, message, correct_answer=0, time_limit=10):
        def check(reaction, user):
            return user != self.user
        reactions_user_time = {}  # Dictionary to store the reactions and the time the user reacted
        losers_list = []
        start_time = tm.time()
        timeout = False
        while not timeout:
            try:
                reaction = await self.wait_for("reaction_add", timeout=0.5, check=check)  # Wait for a reaction
                if reaction[1] not in reactions_user_time and reaction[1] not in losers_list:
                    if self.responses.index(reaction[0].emoji) == correct_answer:
                        reactions_user_time[reaction[1]] = tm.time() - start_time
                    else:
                        losers_list.append(reaction[1])

            except asyncio.TimeoutError:
                pass
            timeout = (tm.time() - start_time) > time_limit  # If the time is more than 10 seconds
        await message.channel.send("Time is up!")
        results = dict(sorted(reactions_user_time.items(), key=lambda item: item[1]))
        return results  # Display the dictionary

