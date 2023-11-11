import os

from Bot.bot import GentleBot

# Load .env file
from dotenv import load_dotenv

load_dotenv()

# load token from env
TOKEN = os.getenv("TOKEN")

# main function
def main():
    bot = GentleBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()