import asyncio
import json
import random
from random import randint

import discord

from games.Game import Game
from models.UserScore import UserScore


class GuessPhraseGame(Game):

    def __init__(self, bot, max_winners=3, time_limit=10):
        super().__init__(bot, max_winners, time_limit)

    async def start(self, ctx):
        file = open('sentences.json', mode='r')
        sentences = json.load(file)['data']
        file.close()
        min_range = min(len(sentences), 20)
        for i in range(min_range):
            index = randint(0, len(sentences) - 1)
            sentence = sentences.pop(index)
            sentence_to_guess = await self.xcode_phrase(sentence)
            msg: discord.Message = await ctx.send(sentence_to_guess)
            winner = None
            while not winner:
                def check(message):
                    return message.author != self.bot.user and msg.channel == message.channel and message.content.lower() == sentence.lower()

                try:
                    response_msg = await self.bot.wait_for('message', check=check, timeout=self.time_limit)
                    winner = response_msg.author
                except asyncio.TimeoutError:
                    sentence_to_guess = await self.xdecode_phrase(sentence, sentence_to_guess)
                    if sentence_to_guess == sentence:
                        await ctx.send(f"Nobody guessed the phrase. The correct phrase was: {sentence}")
                        winner = "Nobody"
                    else:
                        await ctx.send(sentence_to_guess)
            if winner != "Nobody":
                await ctx.send(f"{winner.mention} guessed the phrase!")
                results = {winner: 1}
                await self.register_round_points(results)
        results_string = await self.overall_results_by_points()
        await ctx.send(results_string)

    async def xcode_phrase(self, sentence):
        sentence = list(sentence)
        for i in range(len(sentence)):
            if randint(0, 100) < 65:
                if sentence[i] != ' ':
                    sentence[i] = '#'
        return ''.join(sentence)

    async def xdecode_phrase(self, correct_sentence, coded_sentence):
        sentence = list(correct_sentence)
        decode = list(coded_sentence)
        random_index = random.choice([i for i in range(len(sentence)) if sentence[i] != ' ' and decode[i] == '#'])
        decode[random_index] = sentence[random_index]
        return ''.join(decode)

    async def register_round_points(self, results: dict):
        registered_users = list(map(lambda item: item.user, self.total_points))
        for user, time in results.items():
            if user not in registered_users:
                userscore = UserScore(user, 1)
                self.total_points.append(userscore)
            else:
                index = registered_users.index(user)
                self.total_points[index].points += 1
