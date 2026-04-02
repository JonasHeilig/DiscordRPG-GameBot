import discord
from discord.ext import commands
from bot.database.db_manager import DatabaseManager
from bot.utils.helpers import calculate_ore_rewards, validate_mining_time


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @discord.app_commands.command(name="join-game", description="Trete dem Minigame bei")
    async def join_game(self, interaction: discord.Interaction):
        server_id = interaction.guild.id
        user_id = interaction.user.id
        username = interaction.user.name

        if not self.db.server_exists(server_id):
            embed = discord.Embed(
                title="Server has no Game Session",
                description="This server has no Game Session! Please ask an Admin to start a new Game Session using `/start-game`.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.db.user_in_game(user_id, server_id):
            embed = discord.Embed(
                title="You are already in the Game!",
                description="You have already joined the game. Use `/stats` to view your resources or `/mine` to start mining.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            self.db.add_user_to_game(user_id, server_id, username)

            embed = discord.Embed(
                title="Welcome to the Mining Game!",
                description=f"Hello {interaction.user.mention}, you have successfully joined the mining game! Use the commands below to start mining and check your stats.",
                color=discord.Color.green()
            )
            embed.add_field(name="Possible Commands", value="/mine\n/stats", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Error by Game Entering {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="mine", description="Start mining for ores")
    @discord.app_commands.describe(time="Mining time in minutes (1-480)")
    async def mine(self, interaction: discord.Interaction, time: int):

        server_id = interaction.guild.id
        user_id = interaction.user.id

        if not self.db.user_in_game(user_id, server_id):
            embed = discord.Embed(
                title="You are not in a game!",
                description="Please join the game first using `/join-game`.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        mining_time = validate_mining_time(time)
        if mining_time is None:
            embed = discord.Embed(
                title="Invalid Mining Time!",
                description="Please enter a valid mining time between 1 and 480 minutes.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await interaction.response.defer()

            probs = self.db.get_ore_probabilities(server_id)
            probs_dict = {
                "coal": probs["coal"],
                "iron": probs["iron"],
                "gold": probs["gold"],
                "copper": probs["copper"],
                "diamond": probs["diamond"],
                "emerald": probs["emerald"]
            }
            rewards = calculate_ore_rewards(mining_time, probs_dict)

            for ore_type, amount in rewards.items():
                self.db.add_ore(user_id, server_id, ore_type, amount)

            embed = discord.Embed(
                title="Finish Mining!",
                description=f"You have {mining_time} Minutes in the mine",
                color=discord.Color.gold()
            )

            for ore_type, amount in rewards.items():
                emoji_map = {
                    "coal": "⬛",
                    "iron": "🩶",
                    "gold": "🟨",
                    "copper": "🟧",
                    "diamond": "💎",
                    "emerald": "💚"
                }
                embed.add_field(
                    name=f"{emoji_map.get(ore_type, '•')} {ore_type.capitalize()}",
                    value=f"+{amount}",
                    inline=True
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Error in Mining: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="stats", description="Show your Resources")
    async def stats(self, interaction: discord.Interaction):

        server_id = interaction.guild.id
        user_id = interaction.user.id

        if not self.db.user_in_game(user_id, server_id):
            embed = discord.Embed(
                title="You are not in a game!",
                description="Please join the game first using `/join-game`.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            resources = self.db.get_user_resources(user_id, server_id)

            embed = discord.Embed(
                title=f"Your Resources",
                description=f"Player: {interaction.user.mention}",
                color=discord.Color.blurple()
            )

            emoji_map = {
                "coal": "⬛",
                "iron": "🩶",
                "gold": "🟨",
                "copper": "🟧",
                "diamond": "💎",
                "emerald": "💚"
            }

            for ore_type in ["coal", "iron", "gold", "copper", "diamond", "emerald"]:
                amount = resources[ore_type]
                embed.add_field(
                    name=f"{emoji_map[ore_type]} {ore_type.capitalize()}",
                    value=str(amount),
                    inline=True
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Error by Loading Stats: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Player(bot))