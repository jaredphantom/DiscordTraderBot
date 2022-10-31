# Discord Crypto Trading Bot

**Run discordBot.py after generating a token with the Discord API and adding it to a .env file (named 'DISCORD_TOKEN'), this will allow you to remotely control the trading bot via Discord commands** 

**Commands are prefixed by a '.', they are: start, stop, pause, unpause, buy, sell, report, logs**

**main.py can take a single integer argument which determines the number of coins to scan, e.g. if you pass '5' as the argument then the top 5 volume coins in the last 24 hours will be added to the array of tradeable coins. If using this input format you can also add arguments which represent coins you want to ignore, the tickers must be in lowercase e.g. 'luna'. The below example is to run the program and track 4 coins while ignoring BTC and ETH**
```
> python main.py 4 btc eth
```
**The second format for running main.py is to just use lowercase string arguments specifying which coins you want to trade, the below example is to run the program and trade BTC, ETH, and DOGE**
```
> python main.py btc eth doge
```
**You must set up your own API key from the Binance site, create a .env file with your API and secret key for the bot to fetch. Keys in the .env file must be named 'API_KEY' and 'SECRET_KEY'**

**Create 2 folders called graphs and logs, to store trade performance graphs and logging output respectively**

**All dependencies are in requirements.txt**
```
> pip install -r requirements.txt 
```
