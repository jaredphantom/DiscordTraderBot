#check for MA crossover event
def MAcross(long, short):
    if long[-1] > short[-1] and long[-2] < short[-2]:
        return -1  #short MA cross below long MA (sell signal)
    elif long[-1] < short[-1] and long[-2] > short[-2]:
        return 1  #short MA cross over long MA (buy signal)
    return 0

#check for MACD crossover event
def MACDcross(macd, signal):
    if macd[-1] - signal[-1] > 0 and macd[-2] - signal[-2] < 0:
        return 1 #bullish macd (buy signal)
    elif macd[-1] - signal[-1] < 0 and macd[-2] - signal[-2] > 0:
        return -1 #bearish macd (sell signal)
    return 0

#check if lines are diverging
def diverging(line1, line2):
    array = []
    for num1, num2 in zip(line1, line2):
        array.append(abs(num1 - num2))
    return all(x < y for x, y in zip(array, array[1:]))

#check if lines are converging
def converging(line1, line2):
    array = []
    for num1, num2 in zip(line1, line2):
        array.append(abs(num1 - num2))
    return all(x > y for x, y in zip(array, array[1:]))

#to be used with numpy arrays and talib
def oldStrategy(closes, adx, rsi, longMA, shortMA):
    if (adx[-1] > 25 and all(x < 25 for x in adx[-10:-2]) and closes[-1] > closes[-50]
        and rsi[-1] < 70 and ((converging(longMA[-3:], shortMA[-3:]) and longMA[-1] > shortMA[-1]) or
                              (diverging(shortMA[-3:], longMA[-3:]) and shortMA[-1] > longMA[-1]))
        and max(closes[-50:]) < 1.01 * min(closes[-50:])):
        return 1 #positive breakout (buy signal)
    elif rsi[-1] > 70:
        return -1 #asset overbought (sell signal)
    return 0

#to be used with tradingview indicators
def momentumStrategy(signal, change, adx, rsi, ma):
    if 30 > adx > 25 and 60 < rsi < 70 and change > 0 and ma and signal == 1:
        return 1 #buy signal
    elif rsi > 70:
        return -1 #sell signal
    return 0

#bollinger bands + rsi strategy
def bollingerStrategy(bbLower, rsi, open, low, close, signal):
    if greenCandle(close, open) and float(low) < bbLower < float(close) and rsi < 40 and signal >= -1:
        return True
    return False

#check if candle is green
def greenCandle(close, open):
    if float(close) > float(open):
        return True
    return False