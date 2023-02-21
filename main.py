from dotenv import load_dotenv
import os

from DiscordBot import Bot

load_dotenv()

bot = Bot(command_prefix='?')

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
