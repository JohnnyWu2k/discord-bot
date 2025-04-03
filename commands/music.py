from discord.ext import commands

@commands.command()
async def music(ctx, *, song: str):
    await ctx.send(f"🎵 Playing song: {song}\n(This is a placeholder. Real music playback requires additional setup.)")
