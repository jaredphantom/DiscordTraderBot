import requests

def requestTop(num, ignore=()):
    num = abs(num)
    url = "https://api.binance.com/api/v3/ticker/24hr"
    data = requests.get(url).json()

    coins = []
    volumes = []

    for item in data:
        if (item["symbol"][-4:] == "USDT" and not "UP" in item["symbol"] and not "DOWN" in item["symbol"]
        and not "BNB" in item["symbol"] and not "USD" in item["symbol"][:-4] and not item["symbol"][:-4].lower() in ignore):
            volumes.append(float(item["quoteVolume"]))

    volumes.sort(reverse=True)
    del volumes[num:]
    print(f"Top {num} coins by 24hr volume:\n")

    for v in volumes:
        for item in data:
            if len(coins) == num:
                break
            if (v == float(item["quoteVolume"]) and item["symbol"][-4:] == "USDT" and not "UP" in item["symbol"]
            and not "DOWN" in item["symbol"] and not "BNB" in item["symbol"] and not "USD" in item["symbol"][:-4]
            and not item["symbol"][:-4].lower() in ignore):
                coins.append(item["symbol"].lower())
                print(f"{item['symbol'][:-4]}: {round(float(item['quoteVolume']), 2)} {item['symbol'][-4:]}")

    return coins

def requestChoice(coins):
    coinArray = []
    for coin in coins:
        cU = coin.upper()
        cL = coin.lower()
        if not "UP" in cU and not "DOWN" in cU and not "BNB" in cU and not "USD" in cU and not f"{cL}usdt" in coinArray:
            coinArray.append(cL+"usdt")
            print(f"{cU}USDT")

    return coinArray
