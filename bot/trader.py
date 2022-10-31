import json, websocket, logging, math, requests, time
from strategy import momentumStrategy, bollingerStrategy
from signals import *
from graph import discGraph
from discord import Webhook, RequestsWebhookAdapter, File
from dotenv import dotenv_values
from binance import Client
from binance.enums import *

#intervals
bigInterval = "1h"
smallInterval = "30m"

#globals
numPositions = 0
losses = 0
numTrades = 0
totalWins = 0
totalChange = 1
fees = 0.0015
webhook = Webhook.from_url(
    "", 
    adapter=RequestsWebhookAdapter())
reconnects = 0

#util functions
def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)

def stepSize(str):
    if str.find(".") == -1:
        return 0
    if str.find("1") - str.find(".") == -1:
        return 0
    return str.find("1") - str.find(".")

def checkBigger(a, b, msg):
    try:
        assert(a > b)
        return True
    except AssertionError:
        logging.error(msg)
    return False

#Trader class contains all values needed to interact with binance api
class Trader:

    def __init__(self, ticker, api, secret, coinArray):
        self._ticker = ticker
        self._coins = coinArray
        self._socket = f"wss://stream.binance.com:9443/ws/{ticker.lower()}@kline_{smallInterval}"
        self._client = Client(api_key=api, api_secret=secret)
        self._buyPrice = 0
        self._quantity = 0
        self._change = 0
        self._position = True
        self._trail = False
        self._trailPrice = 0
        self._stepSize = 0
        self._slippage = 0.9985
        self._takeProfit = 1.02
        self._stopLoss = 0.98
        self._trailingStop = 0.998
        self._ws = None
        self._pause = False
        self._changes = []
        self._wait = True
        self._strat = None

    #websocket functions
    def socketOpen(self, ws):
        global numPositions
        self._stepSize = stepSize(self._client.get_symbol_info(self._ticker.upper())['filters'][2]['stepSize'])
        notional = self.getBalances() * self.getcurrPrice()
        if self._position and (checkBigger(self.getMinQty(), self.getBalances(), f"Minimum Quantity exceeded for {self._ticker.upper()}")
        or checkBigger(self.getMinNot(), notional, f"Minimum Notional exceeded for {self._ticker.upper()}")):
            numPositions -= 1
            if numPositions < 0:
                numPositions = 0
            self._position = False
        elif self._position:
            logging.info(f"Position already open for {self._ticker.upper()}")
        logging.info(f"{self._ticker[:-4].upper()} Connection opened")

    def socketClose(self, ws, *_):
        logging.info(f"{self._ticker[:-4].upper()} Connection closed")
    
    def socketError(self, ws, error):
        logging.error(error)

    def socketMessage(self, ws, message):
        global numPositions, losses
        cjson = json.loads(message)
        candle = cjson["k"]
        candleClosed = candle["x"]
        closePrice = candle["c"]
        openPrice = candle["o"]
        lowPrice = candle["l"]

        #sell if price hits pre-defined cutoffs while candle is still open
        if self._buyPrice != 0:
            self._change = ((float(closePrice) - self._buyPrice) / self._buyPrice) + 1
            self._changes.append(round((self._change - 1) * 100, 2))
            if self._change > self._takeProfit and self._position and not self._trail and not self._pause:
                print("Take Profit triggered!\n")
                self._trail = True
                self._trailPrice = float(closePrice)
            elif self._change < self._stopLoss and self._position and not self._pause:
                self.sell()
                print("Stop Loss triggered!\n")

        #trailing stop loss to protect gains while allowing winners to run
        if self._trail:
            if float(closePrice) > self._trailPrice:
                self._trailPrice = float(closePrice)
            if ((float(closePrice) - self._trailPrice) / self._trailPrice) + 1 < self._trailingStop and self._position and not self._pause:
                self.sell()
                print("Trailing Stop Loss triggered!\n")

        #wait until price consolidation for next buying opportunity
        if candleClosed and self._wait:
            adx = getADX(self._ticker.upper(), smallInterval)
            if adx < 15:
                self._wait = False

        #dynamically changing stops when using bbands strategy
        if candleClosed and not self._pause and self._position and self._strat == "BBANDS":
            bbands = getBBands(self._ticker.upper(), smallInterval)
            bbBasis = bbands[2]
            if self._buyPrice != 0:
                newProfit = (bbBasis - self._buyPrice) / self._buyPrice
                if newProfit < 3 * fees:
                    newProfit = 3 * fees
                newProfit = newProfit * self._buyPrice
                self._takeProfit = (self._buyPrice + newProfit) / self._buyPrice
                self._trailingStop = 1 - ((self._takeProfit - 1) / 10)

        #buy signals
        if candleClosed and not self._pause and (numPositions == 0 or self._position):
            signal = getSignal(self._ticker.upper(), bigInterval)
            change = getChange(self._ticker.upper(), bigInterval)
            ma = getMA(self._ticker.upper(), smallInterval)
            atr = getATR(self._ticker.upper(), smallInterval)
            rsi = getRSI(self._ticker.upper(), smallInterval)
            adx = getADX(self._ticker.upper(), smallInterval)
            bbands = getBBands(self._ticker.upper(), smallInterval)
            bbLower = bbands[1]
            bbBasis = bbands[2]

            #buy when expecting downtrend reversal
            if not self._position and not self._pause and bollingerStrategy(bbLower, rsi, openPrice, lowPrice, closePrice, signal):
                if losses >= 3:
                    logging.info(f"{self._ticker[:-4].upper()} Buy signal ignored: Too many losses")
                else:
                    profit = (bbBasis - (float(closePrice) * (2 - self._slippage))) / (float(closePrice) * (2 - self._slippage))
                    if profit > 3 * fees:
                        self._strat = "BBANDS"
                        self.buy(closePrice, profit * float(closePrice))

            #buy when price breakout upwards
            if not self._position and not self._pause and not self._wait and momentumStrategy(signal, change, adx, rsi, ma) == 1:
                if losses >= 3:
                    logging.info(f"{self._ticker[:-4].upper()} Buy signal ignored: Too many losses")
                else:
                    self._strat = "MOMENTUM"
                    self.buy(closePrice, 2 * atr)

            #sell if rsi overbought
            if momentumStrategy(signal, change, adx, rsi, ma) == -1 and self._position and not self._pause and self._strat != "BBANDS":
                self._trail = True
                self._trailPrice = float(closePrice)

        #if price uptrend already established then wait for next consolidation
        if candleClosed and not self._wait:
            adx = getADX(self._ticker.upper(), smallInterval)
            if adx > 30:
                self._wait = True


    #stream websocket data
    def listen(self):
        global numPositions, reconnects
        if self.getName() == self._coins[0][:-4].lower():
            numPositions = len(self._coins)
    
        while True:
            self._ws = websocket.WebSocketApp(self._socket, 
                                    on_open=self.socketOpen, 
                                    on_close=self.socketClose, 
                                    on_message=self.socketMessage, 
                                    on_error=self.socketError)

            self._ws.run_forever()

            if self._ws is None:
                break

            reconnects += 1
            time.sleep(math.log(reconnects))

    #open a new position 
    def buy(self, price, atr=0):
        global numPositions
        maxBuy = self.all_in(float(price))
        logging.info(f"Attempt to buy {self._ticker[:-4].upper()}: {maxBuy:.{self._stepSize}f}")
        if checkBigger(maxBuy, self.getMinQty(), "Maximum purchase amount below minimum quantity"):
            order = self.tryOrder(SIDE_BUY, maxBuy)

            if order:
                webhook.send(f"Buy {self._ticker[:-4].upper()} @ ${order['fills'][0]['price']}")
                self._buyPrice = float(order['fills'][0]['price'])
                numPositions += 1
                self._position = True
                self._quantity = maxBuy
                if atr != 0:
                    self._stopLoss = (self._buyPrice - atr) / self._buyPrice
                    self._takeProfit = (self._buyPrice + atr) / self._buyPrice
                    self._trailingStop = 1 - ((self._takeProfit - 1) / 10)
                webhook.send(f"SL: ${self._buyPrice * self._stopLoss:.8f}\nTP: ${self._buyPrice * self._takeProfit:.8f}")
                webhook.send(f"Strategy: {self._strat}")
            else:
                self.setStrat(None)

    #close an open position
    def sell(self):
        global numPositions, losses, numTrades, totalWins, totalChange
        balance = truncate(self.getBalances(), self._stepSize)
        logging.info(f"Attempt to sell {self._ticker[:-4].upper()}: {balance:.{self._stepSize}f}")
        order = self.tryOrder(SIDE_SELL, balance)

        if order:
            numPositions -= 1
            if numPositions < 0:
                numPositions = 0
            self._position = False
            self._trail = False
            self._trailPrice = 0
            if self._buyPrice != 0:
                self._change = ((float(order['fills'][0]['price']) - self._buyPrice) / self._buyPrice) + 1 - fees
                self._changes.append(round((self._change - 1) * 100, 2))
                totalChange = totalChange * self._change
                webhook.send(
                    f"Sell {self._ticker[:-4].upper()} @ ${order['fills'][0]['price']}: {round((self._change - 1) * 100, 4)}% P/L")
                webhook.send(
                    f"Money made/lost from trade: ${round((self._quantity * self._buyPrice * self._change) - (self._quantity * self._buyPrice), 2)}")
                discGraph(self._changes, self.getName(), webhook)
                self._changes = []
                self._strat = None
                self._buyPrice = 0
                self._quantity = 0
                numTrades += 1
                if self._change < 1:
                    losses += 1
                else:
                    losses = 0
                    totalWins += 1
            else:
                webhook.send(f"Sell {self._ticker[:-4].upper()} @ ${order['fills'][0]['price']}")

    #attempts to do a buy/sell order
    def tryOrder(self, side, amount, order_type=ORDER_TYPE_MARKET):
        try:
            amount = f"{amount:.{self._stepSize}f}"
            order = self._client.create_order(symbol=self._ticker.upper(), side=side, type=order_type, quantity=amount)
            logging.info(order)
        except Exception as e:
            logging.error(e)
            return False

        return order

    #get minimum trade quantity for ticker
    def getMinQty(self):
        info = self._client.get_symbol_info(self._ticker.upper())
        return float(info['filters'][2]['minQty'])

    #get minimum notional value for ticker
    def getMinNot(self):
        info = self._client.get_symbol_info(self._ticker.upper())
        return float(info['filters'][3]['minNotional'])

    #get current price for ticker
    def getcurrPrice(self):
        url = requests.get(f'https://api.binance.com/api/v1/ticker/price?symbol={self._ticker.upper()}')
        data = url.json()
        return float(data["price"])

    #get wallet balances for relevant tickers
    def getBalances(self):
        account = self._client.get_account()
        balances = account["balances"]

        for b in balances:
            if b["asset"] == self._ticker[:-4].upper() and self._position:
                return float(b["free"])
            elif b["asset"] == self._ticker[-4:].upper() and not self._position:
                return float(b["free"])
            
    #calculate maximum purchase amount
    def all_in(self, price):
        balance = self.getBalances()
        buy = balance / price
        if checkBigger(len(self._coins), numPositions, "Maximum open positions already reached"):
            amount = (1 / (len(self._coins) - numPositions)) * buy * self._slippage
            #amount = buy * self._slippage
            if self._stepSize == 0:
                return math.floor(amount)
            return truncate(amount, self._stepSize)
        return 0

    #manually close websocket connection
    def closeConn(self):
        temp_ws, self._ws = self._ws, None
        temp_ws.close()

    #return the coin name for current trader object
    def getName(self):
        return self._ticker[:-4].lower()

    #return step size of coin
    def getStep(self):
        return self._stepSize

    #return the position status of coin
    def checkPosition(self):
        return self._position

    #return number of currently open positions
    def countPositions(self):
        return numPositions

    #pause trading for this coin
    def pause(self):
        if not self._pause:
            self._pause = True
            print(f"\n{self._ticker[:-4].upper()} trading paused")
            logging.info(f"{self._ticker[:-4].upper()} trading paused")

    #unpause trading for this coin
    def unpause(self):
        if self._pause:
            self._pause = False
            print(f"\n{self._ticker[:-4].upper()} trading resumed")
            logging.info(f"{self._ticker[:-4].upper()} trading resumed")

    #pause trading for this coin (send to discord)
    def pauseDiscord(self):
        if not self._pause:
            self._pause = True
            webhook.send(f"\n{self._ticker[:-4].upper()} trading paused")
            logging.info(f"{self._ticker[:-4].upper()} trading paused")

    #unpause trading for this coin (send to discord)
    def unpauseDiscord(self):
        if self._pause:
            self._pause = False
            webhook.send(f"\n{self._ticker[:-4].upper()} trading resumed")
            logging.info(f"{self._ticker[:-4].upper()} trading resumed")

    #output trading session summary for all coins
    def printReport(self):
        print("\n----------------------------------------------------------------")
        print(f"Total trades: {numTrades}")
        if numTrades > 0:
            print(f"Win rate: {round((totalWins / numTrades) * 100, 2)}%")
            print(f"Overall P/L: {round(((totalChange - 1) * 100) / len(self._coins) * self._slippage**len(self._coins), 4)}%")
        print("----------------------------------------------------------------")

    #send trading session summary to discord via webhook
    def sendReport(self):
        if numTrades > 0:
            webhook.send(f"Total trades: {numTrades}"
                        +f"\nWin rate: {round((totalWins / numTrades) * 100, 2)}%"
                        +f"\nOverall P/L: {round(((totalChange - 1) * 100) / len(self._coins) * self._slippage**len(self._coins), 4)}%")
        else:
            webhook.send(f"Total trades: {numTrades}")

    #output position status for this coin
    def status(self):
        print("\n----------------------------------------------------------------")
        print(f"{self.getName().upper()}")
        if self._position:
            print("Position Open")
            if self._buyPrice != 0:
                print(f"Current P/L: {round((self._change - 1) * 100, 4)}%")
                print(f"Stop Loss: {round((self._stopLoss - 1) * 100, 4)}%")
                print(f"Take Profit: {round((self._takeProfit - 1) * 100, 4)}%")
                print(f"Trailing Stop Loss: {round((self._trailingStop - 1) * 100, 4)}%")
        else:
            print("No Position")
        print("----------------------------------------------------------------")

    #send log file to discord via webhook
    def sendLogs(self):
        path = "logs/trader.log"
        with open(path, 'rb') as f:
            file = File(f)
        webhook.send(file=file)

    #set strategy variable
    def setStrat(self, strategy):
        self._strat = strategy
 
#get sensitive data from environment file       
def getEnv():
    env = dotenv_values(".env")
    api = env["API_KEY"]
    secret = env["SECRET_KEY"]

    return api, secret
