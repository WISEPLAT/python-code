from twitchio.ext import commands
import twitch_creds
import client

bot = commands.Bot(
    token=twitch_creds.TMI_TOKEN,
    client_id=twitch_creds.CLIENT_ID,
    nick=twitch_creds.BOT_NICK,
    prefix=twitch_creds.BOT_PREFIX,
    initial_channels=[twitch_creds.CHANNEL]
)


@bot.command(name='sell')
async def sell(ctx, ticker):
    # send signal to sell
    if client.get_figi(ticker) in client.get_current_stocks():
        try:
            client.sell(ticker)
            await ctx.send(f'{ctx.author.name} {ticker.upper()} sold')
        except:
            await ctx.send(f'{ctx.author.name} *ошибка*')
    else:
        await ctx.send(f'{ctx.author.name} Чтобы продать {ticker.upper()} - нужно иметь его в портфеле')


@bot.command(name='buy')
async def buy(ctx, ticker):
    # send signal to buy
    try:
        client.buy(ticker)
        await ctx.send(f'{ctx.author.name} {ticker.upper()} bought')
    except:
        await ctx.send(f'{ctx.author.name} *ошибка*')


if __name__ == '__main__':
    bot.run() 
