import discord
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN
from bot.database.db_manager import DatabaseManager

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
db = DatabaseManager()


@bot.event
async def on_ready():
    print(f"Bot Booted as: {bot.user}")
    print(f"In {len(bot.guilds)} Servern active")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} Slash Commands synced")
    except Exception as e:
        print(f"Error by synce: {e}")


async def load_cogs():
    cogs = ['bot.cogs.player', 'bot.cogs.admin']
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Cog load: {cog}")
        except Exception as e:
            print(f"Error by loading {cog} cog: {e}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
