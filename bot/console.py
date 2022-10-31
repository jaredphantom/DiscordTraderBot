import logging
import trader as t
from signals import indicators, getATR

class Console:

    def __init__(self, traders):
        self._traders = traders

    def run(self):
        errorMsg = ("\nCommand List (x = coin e.g. 'btc', y = 'all'):\n\n-buy x/y\n-sell x/y\n-pause x/y\n-unpause x/y" +
        "\n-price x/y\n-indicators x/y\n-status x/y\n-report\n-positions\n-exit")
        tDict = {}
        for trader in self._traders:
            tDict[trader.getName()] = trader

        print(errorMsg)

        while True:
            print("")
            userInput = input().lower()
            name = list(userInput.split(" "))[-1]
            command = list(userInput.split(" "))[0]

            if userInput == "exit":
                logging.info("Closing all connections")
                self.exit()
                break
            elif userInput == "report":
                self.report()
            elif userInput == "positions":
                self.positions()
            elif userInput == "report_discord":
                self.reportDisc()
            elif userInput == "logs_discord":
                self.logsDisc()

            elif name == "all" and name != command:

                if command == "pause":
                    for trader in self._traders:
                        self.cPause(trader)
                elif command == "unpause":
                    for trader in self._traders:
                        self.cUnpause(trader)
                elif command == "pause_discord":
                    for trader in self._traders:
                        self.cPauseDisc(trader)
                elif command == "unpause_discord":
                    for trader in self._traders:
                        self.cUnpauseDisc(trader)
                elif command == "buy" or command == "buy_discord":
                    for trader in self._traders:
                        self.cBuy(trader)
                elif command == "sell" or command == "sell_discord":
                    for trader in self._traders:
                        self.cSell(trader)
                elif command == "status":
                    for trader in self._traders:
                        self.status(trader)
                elif command == "price":
                    for trader in self._traders:
                        self.price(trader)
                elif command == "indicators":
                    for trader in self._traders:
                        self.printIndicators(trader)

                else:
                    print(errorMsg)

            elif name in tDict.keys() and name != command:

                if command == "pause":
                    self.cPause(tDict[name])
                elif command == "unpause":
                    self.cUnpause(tDict[name])
                elif command == "pause_discord":
                    self.cPauseDisc(tDict[name])
                elif command == "unpause_discord":
                    self.cUnpauseDisc(tDict[name])
                elif command == "buy" or command == "buy_discord":
                    self.cBuy(tDict[name])
                elif command == "sell" or command == "sell_discord":
                    self.cSell(tDict[name])
                elif command == "status":
                    self.status(tDict[name])
                elif command == "price":
                    self.price(tDict[name])
                elif command == "indicators":
                    self.printIndicators(tDict[name])
                
                else:
                    print(errorMsg)

            else:
                print(errorMsg)

    def exit(self):
        for trader in self._traders:
            trader.closeConn()

    def report(self):
        self._traders[0].printReport()

    def reportDisc(self):
        self._traders[0].sendReport()
    
    def logsDisc(self):
        self._traders[0].sendLogs()
    
    def status(self, trader):
        trader.status()

    def positions(self):
        print("\n" + str(self._traders[0].countPositions()) + " open positions")
        for trader in self._traders:
            if trader.checkPosition():
                print(trader.getName())

    def cPause(self, trader):
        trader.pause()

    def cUnpause(self, trader):
        trader.unpause()

    def cPauseDisc(self, trader):
        trader.pauseDiscord()

    def cUnpauseDisc(self, trader):
        trader.unpauseDiscord()

    def cBuy(self, trader):
        if not trader.checkPosition():
            trader.setStrat("MANUAL")
            trader.buy(trader.getcurrPrice(), 2 * getATR(f"{trader.getName().upper()}USDT", t.smallInterval))

    def cSell(self, trader):
        if trader.checkPosition():
            trader.sell()

    def price(self, trader):
        print(f"\n{trader.getName()}: {trader.getcurrPrice():.8f}")

    def printIndicators(self, trader):
        indicators(f"{trader.getName().upper()}USDT", t.smallInterval, t.bigInterval)
