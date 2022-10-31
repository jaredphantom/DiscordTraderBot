import wexpect
from trader import webhook
from discord.ext import commands
from dotenv import dotenv_values

#get sensitive data from environment file
def discEnv():
    env = dotenv_values(".env")
    token = env["DISCORD_TOKEN"]

    return token

bot = commands.Bot(command_prefix=".")
my_id = 0
process = None

@bot.command()
async def start(ctx, *args):
    global process
    if ctx.message.author.id == my_id and process is None and len(args) > 0:
        arguments = " ".join(args)
        cmd = "python main.py " + arguments
        process = wexpect.spawn(cmd)

@bot.command()
async def stop(ctx):
    global process
    if ctx.message.author.id == my_id and process is not None:
        process.sendline("exit")
        process.wait()
        process = None
        webhook.send("Disconnected")

@bot.command()
async def report(ctx):
    if ctx.message.author.id == my_id and process is not None:
        process.sendline("report_discord")

@bot.command()
async def logs(ctx):
    if ctx.message.author.id == my_id and process is not None:
        process.sendline("logs_discord")

@bot.command()
async def pause(ctx, coin):
    if ctx.message.author.id == my_id and process is not None:
        process.sendline(f"pause_discord {coin}")

@bot.command()
async def unpause(ctx, coin):
    if ctx.message.author.id == my_id and process is not None:
        process.sendline(f"unpause_discord {coin}")

@bot.command()
async def buy(ctx, coin):
    if ctx.message.author.id == my_id and process is not None:
        process.sendline(f"buy_discord {coin}")

@bot.command()
async def sell(ctx, coin):
    if ctx.message.author.id == my_id and process is not None:
        process.sendline(f"sell_discord {coin}")

bot.run(discEnv())
