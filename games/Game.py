from models.UserScore import UserScore


class Game:
    def __init__(self, bot, max_winners=3, time_limit=10):
        self.total_points = []
        self.max_winners = max_winners
        self.time_limit = time_limit
        self.bot = bot

    async def register_round_points(self, results: dict):
        registered_users = list(map(lambda item: item.user, self.total_points))
        for user, time in results.items():
            if user not in registered_users:
                userscore = UserScore(user, 1 + 1/time)
                self.total_points.append(userscore)
            else:
                index = registered_users.index(user)
                self.total_points[index].points += 1 + 1/time

    async def overall_results_by_points(self):
        total_points_sorted = list(reversed(sorted(self.total_points, key=lambda item: item.points)))

        if len(total_points_sorted) == 0:
            return "No winners for this game!"

        positions_array = [f"{i + 1}. {str(total_points_sorted[i])}\n" for i in range(len(total_points_sorted))]

        max_winners = min(self.max_winners, len(total_points_sorted))
        return "".join(positions_array[:max_winners])

    async def round_results_by_time(self, results: list[UserScore]):
        if len(results) == 0:
            return "No one got it right!"

        results_sorted = list(reversed(sorted(results, key=lambda item: item.points)))

        positions_array = [f"{i+1}. {str(results_sorted[i])}\n"for i in range(len(results_sorted))]

        return "".join(positions_array[:min(self.max_winners, len(results_sorted))])