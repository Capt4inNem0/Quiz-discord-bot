import discord


class UserScore:

    def __init__(self, user: discord.User, points=0.0, points_type="points"):
        self.user = user
        self.points = points
        self.points_type = points_type

    def __str__(self):
        return f"{self.user.mention} - {self.points:.2f} {self.points_type}."
