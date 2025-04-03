from discord.ext import commands

@commands.command()
async def search(ctx, *, query: str):
    await ctx.send(f"🔍 Searching for: {query}\n(Summary feature placeholder)")
