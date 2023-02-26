import json
from random import randint

from games.Game import Game


class GuessPhraseGame(Game):

    def __init__(self, bot, max_winners=3, time_limit=10):
        super().__init__(bot, max_winners, time_limit)

    async def start(self, ctx):
        file = open('sentences.json', mode='r')
        sentences = json.load(file)['data']
        file.close()
        min_range = min(len(sentences), 20)
        total_points = {}
        for i in range(min_range):
            index = randint(0, len(sentences) - 1)
            sentence = sentences[index]
            sentence_to_guess = await self.xcode_phrase(sentence['sentence'])

            sentences.pop(index)
            results = 0
            for user, time in results.items():
                if user not in total_points:
                    total_points[user] = 0
                total_points[user] += 1

    async def xcode_phrase(self, sentence):
        sentence = sentence.split()
        for i in range(len(sentence)):
            if randint(0, 100) < 60:
                if sentence[i] != ' ':
                    sentence[i] = 'X'
        return ''.join(sentence)