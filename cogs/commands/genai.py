import discord
from discord.ext import commands
import google.generativeai as genai

class GenAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        genai.configure(api_key="AIzaSyBfCnM9UpPVdKuxa3gEoNgrYJhanSIDe4M")
        generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 50000}
        self.model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)

    @commands.command(description="Ask GenAI to answer a question.")
    async def genai(self, ctx, *, question):
        prompt = f"Generate a response to the following user input:\n{question}"
        bot_response = self.model.generate_content([prompt])
        quoted_response = f"""```yaml\n{bot_response.text}\n```"""
        embed = discord.Embed(title="Luka | GenAI Response", description=quoted_response, color=0x977FD7)
        embed.set_footer(text="Made with 💖 by kamiplayzofficial")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(GenAI(bot))
