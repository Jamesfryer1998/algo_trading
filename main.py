import yfinance as yf

try:
    data = yf.download("USDLEV=X", "2024-04-25", "2024-04-29", interval="1m", auto_adjust=True)
    if len(data) == 0:
        raise ValueError("No data available for the specified interval")
except ValueError as e:
    print('This is an Error!!!!!!!')

try:
    data = yf.download("USDLEV=X", "2024-04-25", "2024-04-29", interval="1m", auto_adjust=True)
    if len(data) == 0:
        raise ValueError("No data available for the specified interval")
except ValueError as e:
    print('This is an Error!!!!!!!')

try:
    data = yf.download("USDEUR=X", "2024-04-25", "2024-04-29", interval="1m", auto_adjust=True)
    if len(data) == 0:
        raise ValueError("No data available for the specified interval")
except ValueError as e:
    print('This is an Error!!!!!!!')

print(data)