import trader as t
import console as c
import logging, threading, sys
from request import requestTop, requestChoice

#connect to binance websocket and start trading
if __name__ == "__main__":
    logging.basicConfig(filename="logs/trader.log",
                        filemode="w",
                        format="%(asctime)s | %(levelname)s - %(message)s",
                        datefmt="%d %b %H:%M:%S",
                        level=logging.INFO)

    try:
        coinArray = requestTop(int(sys.argv[1]), (sys.argv[2:]))
    except ValueError:
        coinArray = requestChoice(sys.argv[1:])
    
    traders = []
    threads = []

    for coin in coinArray:
        stream = t.Trader(coin, *t.getEnv(), coinArray)
        traders.append(stream)
        wst = threading.Thread(target=stream.listen)
        threads.append(wst)
        wst.start()
    
    if len(traders) > 0:
        t.webhook.send("Connected")
        c.Console(traders).run()

        for thread in threads:
            thread.join()