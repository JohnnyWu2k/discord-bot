from discord.ext import commands

@commands.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=3)

@clear.error
async def clear_error(ctx, error):
    await ctx.send("🚫 You don't have permission to use this.")
