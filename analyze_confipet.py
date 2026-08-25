import numpy as np
import pandas as pd
from backend.app.core.data_engine import data_engine
from backend.app.core.indicator_engine import compute_all_indicators, rsi, macd, bollinger_bands, atr, ema
from backend.app.strategies import STRATEGY_REGISTRY
from backend.app.backtester.engine import BacktestEngine
from backend.app.backtester.analytics import compute_performance_metrics

ticker = "CONFIPET.NS"
print(f"[*] Fetching historical market data for {ticker} (Confidence Petroleum India Ltd)...")

df = data_engine.fetch_ticker_data(ticker, period="2y", interval="1d")
if df is None:
    # Try BSE ticker
    ticker = "CONFIPET.BO"
    df = data_engine.fetch_ticker_data(ticker, period="2y", interval="1d")

if df is None:
    print(f"✗ Could not fetch data for CONFIPET")
    exit(1)

data = compute_all_indicators(df)
macd_line, sig_line, hist = macd(data['Close'])
data['MACD'] = macd_line
data['MACD_Signal'] = sig_line
data['MACD_Hist'] = hist

latest = data.iloc[-1]
prev = data.iloc[-2]
prev5 = data.iloc[-5]

cmp = float(latest['Close'])
open_p = float(latest['Open'])
high_p = float(latest['High'])
low_p = float(latest['Low'])
prev_close = float(prev['Close'])
change_pct = ((cmp - prev_close) / prev_close) * 100.0

ema20 = float(latest['EMA_20'])
ema50 = float(latest['EMA_50'])
ema100 = float(latest['EMA_100'])
ema200 = float(latest['EMA_200'])
rsi_val = float(latest['RSI_14'])
atr_val = float(latest['ATR_14'])
vol = float(latest['Volume'])
vol_sma = float(latest['Vol_SMA20'])
vol_ratio = float(latest['Vol_Ratio'])
bb_upper = float(latest['BB_Upper'])
bb_mid = float(latest['BB_Middle'])
bb_lower = float(latest['BB_Lower'])
bb_width = float(latest['BB_Width'])

high_52w = float(data['High'].iloc[-252:].max())
low_52w = float(data['Low'].iloc[-252:].min())
high_20d = float(data['High'].iloc[-20:].max())
low_20d = float(data['Low'].iloc[-20:].min())

print("="*60)
print(f"  📊 QUANTITATIVE PROFILE: {ticker} (Confidence Petroleum)")
print("="*60)
print(f"Current Price (CMP):   ₹{cmp:.2f} ({change_pct:+.2f}%)")
print(f"52-Week Range:         ₹{low_52w:.2f} - ₹{high_52w:.2f}")
print(f"20-Day Range:          ₹{low_20d:.2f} - ₹{high_20d:.2f}")
print(f"Daily ATR (Volatility): ₹{atr_val:.2f} ({(atr_val/cmp)*100:.2f}% daily range)")
print("-" * 60)
print(f"Moving Averages:")
print(f"  • 20 EMA:   ₹{ema20:.2f}  (Price vs 20 EMA:  {((cmp-ema20)/ema20)*100:+.2f}%)")
print(f"  • 50 EMA:   ₹{ema50:.2f}  (Price vs 50 EMA:  {((cmp-ema50)/ema50)*100:+.2f}%)")
print(f"  • 100 EMA:  ₹{ema100:.2f} (Price vs 100 EMA: {((cmp-ema100)/ema100)*100:+.2f}%)")
print(f"  • 200 EMA:  ₹{ema200:.2f} (Price vs 200 EMA: {((cmp-ema200)/ema200)*100:+.2f}%)")
print("-" * 60)
print(f"Momentum & Oscillators:")
print(f"  • RSI (14):     {rsi_val:.1f} ({'Oversold' if rsi_val<35 else 'Bullish Momentum' if rsi_val>55 else 'Neutral / Consolidating'})")
print(f"  • MACD:         {float(latest['MACD']):.2f} (Signal: {float(latest['MACD_Signal']):.2f}, Hist: {float(latest['MACD_Hist']):+.2f})")
print(f"  • Bollinger:    Upper: ₹{bb_upper:.2f} | Mid: ₹{bb_mid:.2f} | Lower: ₹{bb_lower:.2f} (Width: {bb_width:.1f}%)")
print(f"  • Volume (20D): {vol:,.0f} vs Avg {vol_sma:,.0f} (Ratio: {vol_ratio:.2f}x)")
print("="*60)

# Check Strategy Setups
print("\n🔍 EVALUATING SWING STRATEGY SETUPS:")
for s_id, s in STRATEGY_REGISTRY.items():
    res = s.evaluate_setup(df, ticker)
    if res:
        print(f"  ✓ {s.name}: TRIGGERED! (Score: {res['score']}/100)")
        print(f"    - Entry: ₹{res['close']:.2f} | Stop Loss: ₹{res['stop_loss']:.2f} | Target 1: ₹{res['target_1']:.2f} | Target 2: ₹{res['target_2']:.2f}")
        print(f"    - Setup Note: {res['setup_summary']}")
    else:
        print(f"  ✗ {s.name}: Not Active on current bar")

# Run historical backtest of Trend Pullback on CONFIPET
print("\n📈 HISTORICAL SWING BACKTEST (Last 2 Years on CONFIPET):")
engine = BacktestEngine(initial_capital=200000, risk_per_trade_pct=1.5)
sim = engine.run_single(ticker, df, strategy_id="trend_pullback")
metrics = compute_performance_metrics(sim["trades"], sim["equity_curve"], 200000)
print(f"  • Strategy: Trend-Pullback (20 EMA)")
print(f"  • Total Trades: {metrics['total_trades']}")
print(f"  • Win Rate: {metrics['win_rate']}% ({metrics['winning_trades']}W / {metrics['losing_trades']}L)")
print(f"  • Profit Factor: {metrics['profit_factor']}")
print(f"  • Net Return: {metrics['net_profit_pct']}% (₹{metrics['net_profit']:,.2f})")
print(f"  • Max Drawdown: {metrics['max_drawdown_pct']}%")

# Print recent 10 daily candles
print("\n📋 RECENT 10 TRADING SESSIONS:")
recent_df = data[['Open', 'High', 'Low', 'Close', 'Volume', 'EMA_20', 'RSI_14']].iloc[-10:].copy()
recent_df.index = [d.strftime('%Y-%m-%d') for d in recent_df.index]
print(recent_df.to_string())

