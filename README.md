# BauerVest
**Time in the market, measured.**

BauerVest is an investment analytics app that answers three questions an investor should ask:
*Is this a healthy company? What would investing in it have earned me? And what does waiting to invest cost me?*

<!-- Add a screenshot: upload preview.png to this repo and replace this line with: ![BauerVest](preview.png) -->

## Features
- **Look Back** — backtests monthly investing in up to 3 stocks against the S&P 500, with a lump sum, dividend reinvestment, yearly raises, and an employer 401(k) match. Reports the money-weighted return (IRR) and each stock's CAGR.
- **Look Ahead** — projects "start now vs. start later" to retirement and puts a dollar value on every year of waiting, in today's or future dollars.
- **Goal Planner** — solves for the monthly contribution needed to reach a target by a chosen age.
- **Monte Carlo** — simulates thousands of possible markets to show the range of outcomes and the probability of reaching your goal.
- **Health Check** — grades each company A–F on liquidity, profitability, return on equity, leverage, and revenue growth using its latest 10-K data from SEC EDGAR.
- **Risk Lens** — volatility, max drawdown, best/worst years, and return-per-unit-of-risk.

## Methods
- Monthly purchases at the first trading-day price; dividends reinvested at month-end.
- Total-return index: (Priceₜ + Dividendₜ) ÷ Priceₜ₋₁.
- Employer match = match rate × min(contribution, cap % × salary ÷ 12).
- Projection: Balanceₘ₊₁ = (Balanceₘ + contributions) × (1 + r)^(1/12); inflation-adjusted values divide by (1 + inflation)^years.
- Goal and IRR solved numerically by bisection.

## Tech
Python · pandas · NumPy · Plotly · Streamlit · SEC EDGAR XBRL API · Yahoo Finance (yfinance)

## Run it locally
```bash
pip install -r requirements.txt
streamlit run bauervest.py
```

---
Designed & built by **Carissa Bauer** · Corporate Finance, Clemson University
*For educational purposes only. Not investment advice.*
