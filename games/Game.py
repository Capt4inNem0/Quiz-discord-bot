
class Game:
    def __init__(self, bot, max_winners=3, time_limit=10):
        self.max_winners = max_winners
        self.time_limit = time_limit
        self.bot = bot
