import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, title, description=None, color=0x3498DB):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.timestamp = datetime.datetime.now()
        return embed

    @commands.hybrid_command(name='ping', description='Check bot latency')
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! **{round(self.bot.latency*1000)}ms**")

    @commands.command(name='sync')
    @commands.is_owner()
    async def sync(self, ctx):
        msg = await ctx.send("🔄 Syncing...")
        try:
            synced = await self.bot.tree.sync()
            await msg.edit(content=f"✅ Synced {len(synced)} slash commands!")
        except Exception as e:
            await msg.edit(content=f"❌ Sync failed: {e}")

    @commands.hybrid_command(name='help', description='View available commands')
    async def help(self, ctx):
        embed = self.create_embed("🤖 Bot Commands")
        embed.add_field(name="🧠 AI", value="`>exec <request>` - Generate and run code (Owner Only)", inline=False)
        embed.add_field(name="🔧 Utility", value="`/ping` - Check latency\n`>sync` - Sync slash commands", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))
