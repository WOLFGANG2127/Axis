import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def main():
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        return

    print("✅ Telegram Token Loaded")

    bot = Bot(token=TOKEN)

    try:
        me = await bot.get_me()

        print("\n========== BOT DETAILS ==========")
        print(f"Bot Name : {me.first_name}")
        print(f"Username : @{me.username}")
        print(f"Bot ID   : {me.id}")
        print("=================================")

        print("\n✅ Telegram API Connection Successful")

    except Exception as e:
        print("\n❌ Telegram API Connection Failed")
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())