# Binance Crypto Trading Bot

**Run main.py to start trading, trader.py contains the Trader class with attributes and methods required to interact with Binance API** 

**main.py can take a single integer argument which determines the number of coins to scan, e.g. if you pass '5' as the argument then the top 5 volume coins in the last 24 hours will be added to the array of tradeable coins. If using this input format you can also add arguments which represent coins you want to ignore, the tickers must be in lowercase e.g. 'luna'. The below example is to run the program and track 4 coins while ignoring BTC and ETH**
```
> python main.py 4 btc eth
```
**The second format for running main.py is to just use lowercase string arguments specifying which coins you want to trade, the below example is to run the program and trade BTC, ETH, and DOGE**
```
> python main.py btc eth doge
```
**You must set up your own API key from the Binance site, create a .env file with your API and secret key for the bot to fetch. Keys in the .env file must be named 'API_KEY' and 'SECRET_KEY'**

**All dependencies are in requirements.txt**
```
> pip install -r requirements.txt 
```