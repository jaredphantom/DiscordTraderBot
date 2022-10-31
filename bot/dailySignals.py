import signals, request, time, requests
from discord import Webhook, RequestsWebhookAdapter

#get current price for ticker
def getcurrPrice(coin):
    url = requests.get(f'https://api.binance.com/api/v1/ticker/price?symbol={coin.upper()}')
    data = url.json()
    return float(data["price"])

webhook = Webhook.from_url(
    "",
    adapter=RequestsWebhookAdapter())

while True:
    coins = request.requestTop(5)
    signalArray = []
    msg = ":fire: Daily Signals - Top 5 Volume Coins :fire:\n"

    for coin in coins:
        signalArray.append(signals.getSignal(coin.upper()))

    for c, s in zip(coins, signalArray):
        if s == 1:
            msg += (f"\n{c[:-4].upper()} @ ${getcurrPrice(c):.8f} -> :green_circle:\n")
        elif s == -1:
            msg += (f"\n{c[:-4].upper()} @ ${getcurrPrice(c):.8f} -> :red_circle:\n")
        else:
            msg += (f"\n{c[:-4].upper()} @ ${getcurrPrice(c):.8f} -> :yellow_circle:\n")

    webhook.send(msg)
    time.sleep(86400)
