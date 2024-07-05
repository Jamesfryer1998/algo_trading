# Algo Trading Python App

Welcome to the Algo Trading Python App! This application provides a platform for implementing and testing various algorithmic trading strategies. Below is a brief overview of its key features and functionalities.

## Features:
### Strategies:
- Implement and test a wide range of trading strategies, from simple moving averages to advanced machine learning algorithms.
### Backtesting:
- Backtest your strategies using historical market data to evaluate their performance over time.
### LiveDataStream:
- Stream real-time market data to execute trading decisions based on up-to-the-minute information.
### BrokerAPI:
- Integrate with different broker APIs to execute trades automatically based on predefined strategies.
### TestBroker:
- Utilize a simulated broker environment for testing and debugging trading algorithms without risking real capital.

Configure your broker API credentials in the config.py file.

## Usage Examples:
### Backtesting:
Select a strategy from the available options.
Input the parameters required for the chosen strategy.
Specify the historical data range for backtesting.
View the performance metrics and visualizations generated after backtesting.

### Live Trading:
Ensure your broker API credentials are correctly configured.
Choose a strategy suitable for live trading.
Monitor the application as it executes trades based on real-time market data.


## Setup
This repo relies upon the use of anaconda (conda) for its environment setup. I have created a environment.yml file you can clone the environment from:

```
conda env create -f environment.yml
conda acivate backtrader
```

Due to the age of backtrader and the advancements from python 2 -> 3, we need to setup the ```ibpy2``` package to use python 3. To do so, run this command:

```
find backtrader/lib/python3.9/site-packages/ib/ -name '*.py' -exec 2to3 -w {} \;
```

## Run
Note: This repo is still in development. The final product will run on a timed basis each day for backtesting.

### Backtesting (Current state)
To run the backtesting navigate to ```alog_trading/backtest.py``` and run this file.
You may also want to change the list of stocks/currencies you wish to backtest.

### Live Trading (Current state)
The current state of live trading is NOT functioning properly.

However, the final product will be running live collecting data from IBKR every 10 seconds. The chosen strategie/s will then be run on a continious basis.
