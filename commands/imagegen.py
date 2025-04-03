from discord.ext import commands
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro-vision")

@commands.command()
async def imagegen(ctx, *, prompt: str):
    await ctx.send(f"🖼️ Generating image for: {prompt}\n(This is a placeholder.)")
