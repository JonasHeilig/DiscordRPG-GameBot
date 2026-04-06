import discord
from discord.ext import commands
from bot.database.db_manager import DatabaseManager
from bot.utils.helpers import generate_token


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @discord.app_commands.command(name="setup", description="Start on your Server the RPG Game")
    async def setup(self, interaction: discord.Interaction):

        server_id = interaction.guild.id
        user_id = interaction.user.id

        if self.db.server_exists(server_id):
            embed = discord.Embed(
                title="Server already registered",
                description="This Server is already registered!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            gamemaster_role = await interaction.guild.create_role(
                name="gamemaster",
                color=discord.Color.gold(),
                permissions=discord.Permissions(administrator=True)
            )

            await interaction.user.add_roles(gamemaster_role)

            self.db.add_server(server_id, user_id)

            embed = discord.Embed(
                title="Server Successfully Registered",
                description=f"This Server is successfully registered!",
                color=discord.Color.green()
            )
            embed.add_field(name="Server ID", value=str(server_id), inline=False)
            embed.add_field(name="Gamemaster", value=interaction.user.mention, inline=False)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Error by Setup: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="auth", description="Generate a Token to Authenticate in the WebUI")
    async def auth(self, interaction: discord.Interaction):

        server_id = interaction.guild.id
        user_id = interaction.user.id

        if not self.db.server_exists(server_id):
            embed = discord.Embed(
                title="This Server is not registered",
                description="This Server is not registered! Please ask an Admin to run the /setup command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        gamemaster_id = self.db.get_server_gamemaster(server_id)
        if gamemaster_id != user_id:
            embed = discord.Embed(
                title="Not Authorized",
                description="Only Gamemasters can use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            token = generate_token()
            self.db.create_gamemaster_token(user_id, server_id, token)

            embed = discord.Embed(
                title="Token Generated",
                description="Your authentication token has been generated! Use this token to log in to the WebUI.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Token",
                value=f"```\n{token}\n```",
                inline=False
            )
            embed.add_field(
                name="WebUI URL",
                value="http://localhost:5505/login",
                inline=False
            )
            embed.set_footer(text="Don't share this Token!")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Error by Generating Error: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))
