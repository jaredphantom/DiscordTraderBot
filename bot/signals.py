from tradingview_ta import TA_Handler

#get overall buy or sell recommendation
def getSignal(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )

    signal = output.get_analysis().summary["RECOMMENDATION"]

    if "BUY" in signal:
        return 1
    elif "SELL" in signal:
        return -1
    return 0

#get RSI value
def getRSI(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )

    return float(output.get_indicators(["RSI"])["RSI"])


#get ADX value
def getADX(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )

    return float(output.get_indicators(["ADX"])["ADX"])


#get price change over specified interval
def getChange(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )

    return float(output.get_indicators(["change"])["change"])


#check if MA is bullish or bearish
def getMA(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )

    ma50 = float(output.get_indicators(["SMA50"])["SMA50"])
    ma20 = float(output.get_indicators(["SMA20"])["SMA20"])

    if ma50 > ma20:
        return False
    return True

#get ATR value
def getATR(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )

    return float(output.get_indicators(["ATR"])["ATR"])

#get bollinger bands
def getBBands(symbol, interval="1d"):
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=interval
    )
    
    upper = float(output.get_indicators(["BB.upper"])["BB.upper"])
    lower = float(output.get_indicators(["BB.lower"])["BB.lower"])
    basis = (upper + lower) / 2

    return upper, lower, basis

#output results for all indicators
def indicators(symbol, smallInterval="1d", bigInterval="1d"):
    signal = getSignal(symbol, bigInterval)
    change = getChange(symbol, bigInterval)
    ma = getMA(symbol, smallInterval)
    atr = getATR(symbol, smallInterval)
    rsi = getRSI(symbol, smallInterval)
    adx = getADX(symbol, smallInterval)

    print("\n----------------------------------------------------------------")
    print(symbol)
    if signal == 1:
        print(f"Recommendation: BUY ({bigInterval})")
    elif signal == -1:
        print(f"Recommendation: SELL ({bigInterval})")
    else:
        print(f"Recommendation: NEUTRAL ({bigInterval})")
    print(f"Change: {change:.2f}% ({bigInterval})")
    print(f"20-MA > 50-MA: {ma} ({smallInterval})")
    print(f"ATR: {atr:.8f} ({smallInterval})")
    print(f"RSI: {rsi:.2f} ({smallInterval})")
    print(f"ADX: {adx:.2f} ({smallInterval})")
    print("----------------------------------------------------------------")
