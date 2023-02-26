import json
import asyncio
import time as tm
from random import randint

from games.Game import Game
from models.Question import Question
from models.UserScore import UserScore


class QuizGame(Game):
    def __init__(self, bot, questions_file_path='questions.json', max_questions=20, max_winners=3, time_limit=10):
        super().__init__(bot, max_winners, time_limit)
        self.options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
        self.results = {}

        self.questions_file_path = questions_file_path
        self.max_questions = max_questions

    async def start(self, ctx):
        file = open(self.questions_file_path, mode='r')
        questions = json.load(file)['data']
        file.close()
        min_range = min(len(questions), self.max_questions)

        for i in range(min_range):
            index = randint(0, len(questions) - 1)
            question = Question(**questions[index])
            questions.pop(index)
            results = await self.ask(ctx, question)
            results_string = await self.round_results_by_time(
                list(map(lambda item: UserScore(item[0], item[1], 'seconds'), results.items())))
            await ctx.send(results_string)
            await self.register_round_points(results)

        await ctx.send("The quiz is over!")
        overall_string = await self.overall_results_by_points()
        await ctx.send(overall_string)

    async def ask(self, ctx, question: Question):
        assert len(question.options) == 4, "There must be 4 answers"
        msg = await ctx.send(str(question))
        asyncio.get_event_loop().create_task(self.add_options_to_message(msg))  # Add reactions to the message
        results = await self.check_responses(msg, question.correct_answer)  # Wait for a reaction
        return results

    async def add_options_to_message(self, msg):
        for emoji in self.options:
            asyncio.get_event_loop().create_task(msg.add_reaction(emoji))

    async def check_responses(self, message, correct_answer=0):
        def check(reaction, user):
            return user != self.bot.user

        reactions_user_time = {}  # Dictionary to store the reactions and the time the user reacted
        losers_list = []
        start_time = tm.time()
        timeout = False
        while not timeout:
            try:
                reaction = await self.bot.wait_for("reaction_add", timeout=0.5, check=check)
                emoji = reaction[0].emoji
                user = reaction[1]

                if user not in reactions_user_time and user not in losers_list:
                    if self.options[correct_answer] == emoji:
                        reactions_user_time[user] = tm.time() - start_time
                    else:
                        losers_list.append(user)

            except asyncio.TimeoutError:
                pass
            timeout = (tm.time() - start_time) > self.time_limit  # If the time is more than 10 seconds
        await message.channel.send("Time is up!")
        return dict(sorted(reactions_user_time.items(), key=lambda item: item[1]))
