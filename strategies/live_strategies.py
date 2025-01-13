
##############################################################################
def RSIOverboughtOversoldStrategy(data_frame, params=(30, 75, 25)):
# def RSIOverboughtOversoldStrategy(data_frame, params=(1, 60, 40)):
    rsi_period, rsi_overbought, rsi_oversold = params

    # Calculate RSI
    delta = data_frame['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Last RSI value
    rsi_value = rsi.iloc[-1]

    if rsi_value >= rsi_overbought:
        signal = 2  # Sell signal
    elif rsi_value <= rsi_oversold:
        signal = 1  # Buy signal
    else:
        signal = 0  # Hold signal

    return signal, rsi_value
##############################################################################


##############################################################################
def SimpleMovingAverageStrategy(data_frame, params=(10, 30)):
    sma_period_fast, sma_period_slow = params

    # Calculate fast and slow SMAs
    sma_fast = data_frame['price'].rolling(window=sma_period_fast).mean()
    sma_slow = data_frame['price'].rolling(window=sma_period_slow).mean()

    # Last values of the SMAs
    sma_fast_value = sma_fast.iloc[-1]
    sma_slow_value = sma_slow.iloc[-1]

    # Determine the signal
    if sma_fast_value > sma_slow_value:
        signal = 1  # Buy signal
    elif sma_fast_value < sma_slow_value:
        signal = -1  # Sell signal
    else:
        signal = 0  # Hold signal

    return signal, sma_fast_value, sma_slow_value
##############################################################################


##############################################################################
def MAcrossover(data_frame, params=(30, 50)):
    sma_fast_period, sma_slow_period = params

    # Calculate fast and slow SMAs
    sma_fast = data_frame['price'].rolling(window=sma_fast_period).mean()
    sma_slow = data_frame['price'].rolling(window=sma_slow_period).mean()

    # Last values of the SMAs
    sma_fast_value = sma_fast.iloc[-1]
    sma_slow_value = sma_slow.iloc[-1]

    # Determine the signal
    if sma_fast_value > sma_slow_value and sma_fast.iloc[-2] < sma_slow.iloc[-2]:
        signal = 1  # Buy signal (crossover)
    elif sma_fast_value < sma_slow_value and sma_fast.iloc[-2] > sma_slow.iloc[-2]:
        signal = -1  # Sell signal (crossunder)
    else:
        signal = 0  # Hold signal

    return signal, sma_fast_value, sma_slow_value
##############################################################################


##############################################################################
def RSI2Strategy(data_frame, params=(2, 10, 90)):
    rsi_period, oversold_level, overbought_level = params

    # Calculate RSI
    delta = data_frame['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Last RSI value
    rsi_value = rsi.iloc[-1]

    # Determine the signal
    if rsi_value < oversold_level:
        signal = 1  # Buy signal
    elif rsi_value > overbought_level:
        signal = -1  # Sell signal
    else:
        signal = 0  # Hold signal

    return signal, rsi_value
##############################################################################


##############################################################################
def BreakoutStrategy(data_frame, params=(20, 0.02, 0.04)):
    breakout_period, stop_loss_pct, take_profit_pct = params

    # Calculate the 'high' column by finding the highest price in the breakout_period
    data_frame['high'] = data_frame['price'].rolling(window=breakout_period).max()

    # Calculate breakout level (highest high in the past period)
    breakout_level = data_frame['high']

    # Get the current close price
    current_price = data_frame['price'].iloc[-1]

    # Calculate stop-loss and take-profit levels
    stop_loss_price = current_price * (1 - stop_loss_pct)
    take_profit_price = current_price * (1 + take_profit_pct)

    # Determine the signal
    if current_price > breakout_level.iloc[-2]:
        signal = 1  # Buy signal (price breaks above breakout level)
    else:
        signal = 0  # Hold signal

    return signal, breakout_level.iloc[-1], stop_loss_price, take_profit_price
##############################################################################


##############################################################################
def BreakdownStrategy(data_frame, params=(20, 0.02, 0.04)):
    breakdown_period, stop_loss_pct, take_profit_pct = params    
    # Calculate the 'low' column by finding the lowest price in the breakdown_period
    data_frame['low'] = data_frame['price'].rolling(window=breakdown_period).min()
    
    # Calculate breakdown level (lowest low in the past period)
    breakdown_level = data_frame['low']

    # Get the current close price
    current_price = data_frame['price'].iloc[-1]

    # Calculate stop-loss and take-profit levels
    stop_loss_price = current_price * (1 + stop_loss_pct)
    take_profit_price = current_price * (1 - take_profit_pct)

    # Determine the signal
    if current_price < breakdown_level.iloc[-2]:
        signal = -1  # Sell signal (price breaks below breakdown level)
    else:
        signal = 0  # Hold signal

    return signal, breakdown_level.iloc[-1], stop_loss_price, take_profit_price
##############################################################################

def strategy_to_string(strategy):
    if strategy == "SimpleMovingAverageStrategy":
        return SimpleMovingAverageStrategy
    elif strategy == "MAcrossover":
        return MAcrossover
    elif strategy == "RSI2Strategy":
        return RSI2Strategy
    elif strategy == "BreakoutStrategy":
        return BreakoutStrategy
    elif strategy == "BreakdownStrategy":
        return BreakdownStrategy
    elif strategy == "RSIOverboughtOversoldStrategy":
        return RSIOverboughtOversoldStrategy

def live_strategy_list():
    return [
        "RSIOverboughtOversoldStrategy",
        "SimpleMovingAverageStrategy", 
        "MAcrossover", 
        "RSI2Strategy",
        "BreakoutStrategy", 
        "BreakdownStrategy"]

STRATEGY_REGISTRY = {
    "SimpleMovingAverageStrategy": SimpleMovingAverageStrategy,
    "MAcrossover": MAcrossover,
    "RSI2Strategy": RSI2Strategy,
    "BreakoutStrategy": BreakoutStrategy,
    "BreakdownStrategy": BreakdownStrategy,
    "RSIOverboughtOversoldStrategy": RSIOverboughtOversoldStrategy
}