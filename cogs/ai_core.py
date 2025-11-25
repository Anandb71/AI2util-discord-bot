import discord
from discord.ext import commands
import os
import datetime
import google.generativeai as genai
import asyncio
from utils.safety import scan_code, extract_code_block

class AICore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
            print("⚠️ GEMINI_API_KEY not found in .env")

    def create_embed(self, title, description=None, color=0x3498DB):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.timestamp = datetime.datetime.now()
        return embed

    @commands.command(name='exec')
    @commands.is_owner()
    async def ai_exec(self, ctx, *, request: str):
        """
        🤖 AI Agent Command
        Generates and executes Discord.py code based on natural language requests.
        """
        if not self.model:
            return await ctx.send("❌ AI not configured. Please check GEMINI_API_KEY.")

        # Initial thinking embed
        thinking_embed = self.create_embed("🤖 AI Agent", "Processing request...", color=0x9B59B6)
        thinking_embed.add_field(name="Request", value=f"```{request}```", inline=False)
        thinking_embed.add_field(name="Status", value="🧠 Thinking...", inline=False)
        thinking_msg = await ctx.send(embed=thinking_embed)

        try:
            # Context Gathering
            channels_info = "\n".join([f"- {c.name} (ID: {c.id}, Type: {c.type})" for c in ctx.guild.channels[:20]])
            roles_info = "\n".join([f"- {r.name} (ID: {r.id})" for r in ctx.guild.roles[:20]])
            
            prompt = f"""
You are an advanced Discord Bot Agent using discord.py.
Your task is to generate Python code to fulfill the user's request.

USER REQUEST: "{request}"

CURRENT CONTEXT:
Server: {ctx.guild.name} (ID: {ctx.guild.id})
Channel: {ctx.channel.name} (ID: {ctx.channel.id})
Author: {ctx.author.name} (ID: {ctx.author.id})

AVAILABLE CHANNELS (first 20):
{channels_info}

AVAILABLE ROLES (first 20):
{roles_info}

RULES:
1. Generate ONLY executable Python code.
2. Use async/await properly.
3. Handle errors gracefully.
4. Use the provided 'ctx' object for Discord operations.
5. Import any needed modules at the start.
6. Make it production-ready and polished.
7. Add helpful feedback messages with embeds.
8. Use the 'create_embed' helper function provided.

⚠️ CRITICAL SECURITY RULE:
DO NOT ATTEMPT TO READ, OPEN, OR ACCESS ANY SOURCE FILES.
You are FORBIDDEN from using open(), file operations, os.listdir, or ANY file system access.
Focus ONLY on Discord bot functionality using the provided ctx and bot objects.

CODE FORMAT:
```python
# Your code here
async def execute():
    # Implementation
    pass

await execute()
```

Generate the code now:"""

            # AI Generation
            response = self.model.generate_content(prompt)
            generated_code = response.text
            code = extract_code_block(generated_code)
            
            # Confirmation
            confirm_embed = self.create_embed("⚠️ Confirm Execution", color=0xFFA500)
            confirm_embed.add_field(name="Request", value=f"```{request}```", inline=False)
            confirm_embed.add_field(name="Generated Code", value=f"```python\n{code[:800]}...\n```" if len(code) > 800 else f"```python\n{code}\n```", inline=False)
            confirm_embed.set_footer(text="React with ✅ to execute or ❌ to cancel")
            
            await thinking_msg.delete()
            confirm_msg = await ctx.send(embed=confirm_embed)
            await confirm_msg.add_reaction("✅")
            await confirm_msg.add_reaction("❌")
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                
                if str(reaction.emoji) == "❌":
                    await confirm_msg.edit(embed=self.create_embed("❌ Cancelled", "Execution cancelled by user.", color=0xFF0000))
                    return
                
                if str(reaction.emoji) == "✅":
                    await confirm_msg.edit(embed=self.create_embed("🚀 Executing...", "Running generated code...", color=0x00FF00))
                    
                    # Safety Check
                    if not scan_code(code):
                        return await ctx.send("⚠️ **SAFETY LOCK:** Dangerous code detected. Execution blocked.")
                    
                    # Execution Environment
                    exec_globals = {
                        'discord': discord,
                        'commands': commands,
                        'ctx': ctx,
                        'bot': self.bot,
                        'create_embed': self.create_embed,
                        'os': os,
                        'datetime': datetime,
                        'asyncio': asyncio
                    }
                    
                    # Execute
                    try:
                        exec(code, exec_globals)
                        await ctx.send("✅ **Execution Complete**")
                    except Exception as e:
                        await ctx.send(f"❌ **Runtime Error:**\n```py\n{e}\n```")

            except asyncio.TimeoutError:
                await confirm_msg.edit(embed=self.create_embed("⏰ Timeout", "Confirmation timed out.", color=0xFF0000))

        except Exception as e:
            await ctx.send(f"❌ **AI Error:** {str(e)}")

async def setup(bot):
    await bot.add_cog(AICore(bot))
