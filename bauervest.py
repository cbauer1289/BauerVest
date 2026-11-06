"""
BauerVest — Time in the market, measured.
An investment analytics studio by Carissa Bauer.

Run on your computer (opens in a new browser tab):
    python -m streamlit run bauervest.py
"""
import datetime as dt
import html
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ───────────────────────────────────────────── personalize here
APP_NAME = "BauerVest"
TAGLINE = "Time in the market, measured."
AUTHOR_LINE = "Designed & built by Carissa Bauer · Corporate Finance · Clemson University"
LINKEDIN_URL = ""         # e.g. "https://www.linkedin.com/in/your-handle"
SEC_CONTACT_EMAIL = ""    # SEC asks apps to identify themselves; put your email here

BENCH = "SPY"
BENCH_NAME = "S&P 500"
TODAY = dt.date.today()

# ───────────────────────────────────────────── palette (midnight · champagne · violet)
BG = "#07070B"
CARD = "#12121B"
CARD2 = "#191924"
LINE = "#262636"
TEXT = "#F5F1E8"
MUTED = "#8E8BA3"
GOLD = "#E8C27A"
VIOLET = "#A08FFF"
TEAL = "#5EEAD4"
ROSE = "#FF8FB1"
SILVER = "#C9C7D6"
GREEN = "#5EE6A0"
RED = "#FF6B81"
ORANGE = "#FFA65C"
SERIES = [GOLD, VIOLET, TEAL]
GRADE_COLOR = {"A": GREEN, "B": TEAL, "C": GOLD, "D": ORANGE, "F": RED, "—": MUTED}

st.set_page_config(page_title=APP_NAME, page_icon="◆", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, label, input, button {{ font-family: 'Inter', sans-serif; }}
[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(1100px 520px at 8% -8%, rgba(160,143,255,.14), transparent 60%),
    radial-gradient(900px 480px at 100% -5%, rgba(232,194,122,.11), transparent 55%),
    {BG};
}}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0D0D14 0%, #0A0A10 100%); border-right: 1px solid {LINE}; }}
[data-testid="stSidebar"] label p {{ color: {MUTED} !important; font-size: 12.5px !important; }}
.block-container {{ padding-top: 2.2rem; max-width: 1320px; }}

.side-brand {{ font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700; color: {TEXT}; margin: 4px 0 2px; }}
.side-brand span {{ color: {GOLD}; font-style: italic; }}
.side-sub {{ color: {MUTED}; font-size: 12px; margin-bottom: 8px; }}
.sec {{ color: {GOLD}; font-size: 11px; font-weight: 700; letter-spacing: .16em; margin: 22px 0 6px;
        padding-top: 14px; border-top: 1px solid {LINE}; }}

.hero {{ padding: 6px 0 22px; }}
.eyebrow {{ color: {GOLD}; font-size: 12px; font-weight: 700; letter-spacing: .28em; }}
.brand {{ font-family: 'Playfair Display', serif; font-size: 64px; line-height: 1.02; font-weight: 700;
          color: {TEXT}; margin: 8px 0 6px; letter-spacing: -.01em; }}
.brand span {{ font-style: italic; background: linear-gradient(90deg, {GOLD}, {ROSE} 55%, {VIOLET});
               -webkit-background-clip: text; background-clip: text; color: transparent; }}
.tagline {{ font-size: 20px; color: {TEXT}; opacity: .92; }}
.byline {{ font-size: 13px; color: {MUTED}; margin-top: 6px; }}
.byline a {{ color: {GOLD}; text-decoration: none; }}

.kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 6px 0 22px; }}
@media (max-width: 1000px) {{ .kpi-row {{ grid-template-columns: repeat(2, 1fr); }} .brand {{ font-size: 46px; }} }}
.kpi {{ background: linear-gradient(160deg, {CARD2}, {CARD}); border: 1px solid {LINE}; border-radius: 18px;
        padding: 18px 20px; position: relative; overflow: hidden; }}
.kpi::after {{ content: ""; position: absolute; inset: 0 0 auto 0; height: 2px;
               background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: .9; }}
.kpi-label {{ color: {MUTED}; font-size: 11px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }}
.kpi-value {{ font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 700; margin-top: 6px; color: var(--accent); }}
.kpi-sub {{ color: {MUTED}; font-size: 12.5px; margin-top: 2px; }}

.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ background: transparent; border-radius: 12px 12px 0 0; padding: 10px 16px; color: {MUTED}; }}
.stTabs [aria-selected="true"] {{ color: {TEXT} !important; background: {CARD}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {GOLD}; }}

.panel {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 18px; padding: 18px 20px; margin-bottom: 14px; }}
.panel h4 {{ font-family: 'Playfair Display', serif; font-size: 22px; margin: 0 0 4px; color: {TEXT}; }}
.note {{ color: {MUTED}; font-size: 13.5px; line-height: 1.55; }}
.insight {{ border-left: 3px solid {GOLD}; background: rgba(232,194,122,.06); border-radius: 0 12px 12px 0;
            padding: 12px 16px; color: {TEXT}; font-size: 14.5px; margin: 6px 0 16px; }}

.tbl {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
.tbl th {{ text-align: right; color: {MUTED}; font-weight: 600; font-size: 11px; letter-spacing: .1em;
           text-transform: uppercase; padding: 10px 12px; border-bottom: 1px solid {LINE}; }}
.tbl th:first-child, .tbl td:first-child {{ text-align: left; }}
.tbl td {{ text-align: right; padding: 12px; border-bottom: 1px solid {LINE}; color: {TEXT};
           font-variant-numeric: tabular-nums; }}
.tbl tr:last-child td {{ border-bottom: none; }}
.dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}

.hc {{ background: linear-gradient(160deg, {CARD2}, {CARD}); border: 1px solid {LINE}; border-radius: 20px; padding: 20px 22px; height: 100%; }}
.hc-top {{ display: flex; justify-content: space-between; align-items: flex-start; }}
.hc-tic {{ font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: {TEXT}; }}
.hc-name {{ color: {MUTED}; font-size: 12.5px; }}
.hc-grade {{ font-family: 'Playfair Display', serif; font-size: 52px; font-weight: 700; line-height: 1; }}
.hc-row {{ display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-top: 1px solid {LINE}; }}
.hc-k {{ color: {TEXT}; font-size: 14px; font-weight: 600; }}
.hc-x {{ color: {MUTED}; font-size: 12px; }}
.hc-v {{ color: {TEXT}; font-size: 15px; font-weight: 600; font-variant-numeric: tabular-nums; margin-right: 10px; }}
.pill {{ display: inline-block; min-width: 30px; text-align: center; border-radius: 999px; padding: 3px 9px;
         font-weight: 700; font-size: 13px; }}
.foot {{ color: {MUTED}; font-size: 12px; text-align: center; margin: 34px 0 10px; padding-top: 18px; border-top: 1px solid {LINE}; }}
</style>
""", unsafe_allow_html=True)


class DataError(Exception):
    pass


# ───────────────────────────────────────────── formatting
def money(x):
    return "—" if x is None or not np.isfinite(x) else f"${x:,.0f}"


def big(x):
    if x is None or not np.isfinite(x):
        return "—"
    a = abs(x)
    if a >= 1e9:
        return f"${x / 1e9:,.2f}B"
    if a >= 1e6:
        return f"${x / 1e6:,.2f}M"
    if a >= 1e4:
        return f"${x / 1e3:,.0f}K"
    return money(x)


def pct(x, d=1):
    return "—" if x is None or not np.isfinite(x) else f"{x * 100:.{d}f}%"


def kpi(label, value, sub, accent):
    return (f'<div class="kpi" style="--accent:{accent}"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>')


def section(text):
    st.markdown(f'<div class="sec">{text}</div>', unsafe_allow_html=True)


def show_chart(fig):
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def style(fig, height=430, money_axis=True, ytitle=None):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        margin=dict(l=8, r=8, t=40, b=8), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)",
                    font=dict(color=MUTED, size=12)),
        hoverlabel=dict(bgcolor=CARD2, bordercolor=LINE, font=dict(color=TEXT)))
    fig.update_xaxes(showgrid=False, linecolor=LINE, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=LINE, zeroline=False, tickfont=dict(color=MUTED), title=ytitle,
                     tickprefix="$" if money_axis else None, tickformat="~s" if money_axis else None)
    return fig


def color_of(t, tickers):
    return SILVER if t == BENCH else SERIES[tickers.index(t) % len(SERIES)]


def label_of(t):
    return f"{BENCH_NAME} ({BENCH})" if t == BENCH else t


# ───────────────────────────────────────────── market data (Yahoo Finance)
@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load_prices(ticker, start):
    import yfinance as yf
    h = yf.Ticker(ticker).history(start=start, auto_adjust=False, actions=True)
    if h is None or h.empty or "Close" not in h:
        raise DataError(f"No price history found for {ticker}")
    idx = pd.to_datetime(h.index)
    if idx.tz is not None:
        idx = idx.tz_convert(None)
    divs = h["Dividends"] if "Dividends" in h else 0.0
    out = pd.DataFrame({"close": h["Close"].astype(float).values,
                        "div": pd.Series(divs, index=h.index).fillna(0).astype(float).values},
                       index=idx.normalize())
    return out[out["close"] > 0].dropna()


# ───────────────────────────────────────────── fundamentals (SEC EDGAR)
SEC_HEADERS = {"User-Agent": f"BauerVest portfolio app {SEC_CONTACT_EMAIL}".strip()}
ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def sec_ticker_map():
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADERS, timeout=20)
    r.raise_for_status()
    return {v["ticker"].upper(): (int(v["cik_str"]), v["title"]) for v in r.json().values()}


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def sec_facts(cik):
    r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json",
                     headers=SEC_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def annual(facts, tags, flow):
    """Annual values for the first available XBRL tags, indexed by fiscal period end."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    rows = []
    for pri, tag in enumerate(tags):
        for r in gaap.get(tag, {}).get("units", {}).get("USD", []):
            if r.get("form") not in ANNUAL_FORMS:
                continue
            end = pd.Timestamp(r["end"])
            if flow:
                if "start" not in r or not 330 <= (end - pd.Timestamp(r["start"])).days <= 400:
                    continue
            rows.append((end, pri, r.get("filed", ""), float(r["val"])))
    if not rows:
        return pd.Series(dtype=float)
    df = pd.DataFrame(rows, columns=["end", "pri", "filed", "val"])
    df = df.sort_values(["end", "pri", "filed"], ascending=[True, True, False]).drop_duplicates("end")
    return df.set_index("end")["val"]


def near(series, when, tol=12):
    if series.empty:
        return np.nan
    gap = np.abs((series.index - when).days)
    i = int(np.argmin(gap))
    return float(series.iloc[i]) if gap[i] <= tol else np.nan


def total(*vals):
    v = [x for x in vals if np.isfinite(x)]
    return float(sum(v)) if v else np.nan


def grade(value, cuts, higher_better=True):
    if value is None or not np.isfinite(value):
        return "—"
    for letter, cut in zip("ABCD", cuts):
        if (value >= cut) if higher_better else (value <= cut):
            return letter
    return "F"


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def health_check(ticker):
    cik, title = sec_ticker_map().get(ticker.replace(".", "-").upper(), (None, None))
    if cik is None:
        return None
    f = sec_facts(cik)
    rev = annual(f, ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
                     "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet"], True)
    ni = annual(f, ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"], True)
    ca = annual(f, ["AssetsCurrent"], False)
    cl = annual(f, ["LiabilitiesCurrent"], False)
    eq = annual(f, ["StockholdersEquity",
                    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], False)
    if rev.empty or eq.empty:
        return None

    fy = rev.index.max()
    bs = eq.index.max()
    revenue, net = float(rev.loc[fy]), near(ni, fy)
    equity = float(eq.loc[bs])

    ltd = near(annual(f, ["LongTermDebt"], False), bs)
    if not np.isfinite(ltd):
        ltd = total(near(annual(f, ["LongTermDebtNoncurrent"], False), bs),
                    near(annual(f, ["LongTermDebtCurrent", "DebtCurrent"], False), bs))
    debt = total(ltd, near(annual(f, ["ShortTermBorrowings"], False), bs),
                 near(annual(f, ["CommercialPaper"], False), bs))

    rev3 = near(rev, fy - pd.DateOffset(years=3), tol=45)
    rev1 = near(rev, fy - pd.DateOffset(years=1), tol=45)
    growth, gyrs = ((revenue / rev3) ** (1 / 3) - 1, 3) if np.isfinite(rev3) and rev3 > 0 else \
        ((revenue / rev1 - 1, 1) if np.isfinite(rev1) and rev1 > 0 else (np.nan, 3))

    cr = near(ca, bs) / near(cl, bs)
    margin = net / revenue if revenue else np.nan
    pos_eq = equity > 0
    roe = net / equity if pos_eq else np.nan
    de = debt / equity if pos_eq else np.nan

    metrics = [
        ("Liquidity", "Current ratio", f"{cr:.2f}×" if np.isfinite(cr) else "—",
         grade(cr, [2.0, 1.5, 1.0, 0.8]), "Can it cover bills due within a year?"),
        ("Profitability", "Net margin", pct(margin), grade(margin, [.20, .10, .05, 0]),
         "Cents of profit kept from each sales dollar"),
        ("Efficiency", "Return on equity", pct(roe) if pos_eq else "n/m",
         grade(roe, [.20, .15, .10, 0]) if pos_eq else "—",
         "Profit generated on shareholders' capital" if pos_eq else "Negative equity (heavy buybacks)"),
        ("Leverage", "Debt-to-equity", f"{de:.2f}×" if pos_eq and np.isfinite(de) else "n/m",
         grade(de, [0.5, 1.0, 2.0, 3.0], higher_better=False) if pos_eq else "—",
         "Borrowed dollars per dollar of equity"),
        ("Growth", f"Revenue growth ({gyrs}-yr CAGR)" if gyrs == 3 else "Revenue growth (1-yr)",
         pct(growth), grade(growth, [.15, .08, .03, 0]), "How fast the top line is expanding"),
    ]
    pts = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    scored = [pts[m[3]] for m in metrics if m[3] in pts]
    gpa = np.mean(scored) if scored else np.nan
    overall = "—" if not np.isfinite(gpa) else ("A" if gpa >= 3.5 else "B" if gpa >= 2.5 else
                                                 "C" if gpa >= 1.5 else "D" if gpa >= 0.75 else "F")
    return {"name": title.title() if title else ticker, "fy": fy, "metrics": metrics,
            "gpa": gpa, "overall": overall}


# ───────────────────────────────────────────── finance engine
def contributions(n, monthly, salary, raise_pct, use_match, match_pct, match_cap):
    """Your monthly contribution and employer match; both step up once a year with raises."""
    g = (1 + raise_pct) ** (np.arange(n) // 12)
    you = monthly * g
    emp = match_pct * np.minimum(you, match_cap * salary * g / 12) if use_match else np.zeros(n)
    return you, emp


def grow(n, lump, you, emp, annual_r):
    """Balance path: contributions go in at the start of each month, then compound monthly."""
    r = (1 + annual_r) ** (1 / 12) - 1
    bal = np.empty(n + 1)
    bal[0] = lump
    for k in range(n):
        bal[k + 1] = (bal[k] + you[k] + emp[k]) * (1 + r)
    return bal


def irr_annual(flows):
    """Money-weighted annual return from monthly cash flows (bisection on NPV)."""
    flows = np.asarray(flows, dtype=float)
    t = np.arange(len(flows))
    def npv(r):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            return np.sum(flows / (1 + r) ** t)
    lo, hi = -0.95, 1.0
    if npv(lo) * npv(hi) > 0:
        return np.nan
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (1 + (lo + hi) / 2) ** 12 - 1


def backtest(px, lump, you, emp, reinvest):
    m = px.index.to_period("M")
    first, last = px["close"].groupby(m).first(), px["close"].groupby(m).last()
    divs = px["div"].groupby(m).sum()
    shares = cash = put_you = put_emp = 0.0
    rows, flows = [], []
    for k, p in enumerate(first.index):
        c_you = you[k] + (lump if k == 0 else 0.0)
        shares += (c_you + emp[k]) / first[p]
        put_you, put_emp = put_you + c_you, put_emp + emp[k]
        flows.append(-(c_you + emp[k]))
        payout = shares * divs[p]
        if reinvest:
            shares += payout / last[p]
        else:
            cash += payout
        rows.append((p.to_timestamp(), shares * last[p] + cash, put_you, put_emp))
    df = pd.DataFrame(rows, columns=["date", "value", "you", "emp"]).set_index("date")
    flows.append(df["value"].iloc[-1])
    return df, irr_annual(flows)


def monte_carlo(n, lump, you, emp, annual_r, vol, sims, seed=42):
    """Simulated balance paths: monthly returns are lognormal, so the median path grows at annual_r."""
    rng = np.random.default_rng(seed)
    growth = np.exp(rng.normal(np.log1p(annual_r) / 12, vol / np.sqrt(12), size=(sims, n)))
    bal = np.empty((sims, n + 1))
    bal[:, 0] = lump
    for k in range(n):
        bal[:, k + 1] = (bal[:, k] + you[k] + emp[k]) * growth[:, k]
    return bal


def risk(px, reinvest):
    c = px["close"]
    d = px["div"] if reinvest else 0.0
    idx = (1 + ((c + d) / c.shift(1) - 1).fillna(0)).cumprod()
    years = max((idx.index[-1] - idx.index[0]).days / 365.25, 1 / 12)
    monthly = idx.groupby(idx.index.to_period("M")).last().pct_change().dropna()
    ye = idx.groupby(idx.index.year).last()
    yearly = pd.concat([pd.Series([1.0], index=[ye.index[0] - 1]), ye]).pct_change().dropna()
    return {"cagr": idx.iloc[-1] ** (1 / years) - 1, "vol": monthly.std() * np.sqrt(12),
            "dd": idx / idx.cummax() - 1, "maxdd": (idx / idx.cummax() - 1).min(),
            "yearly": yearly, "growth": idx}


# ───────────────────────────────────────────── sidebar · inputs
with st.sidebar:
    st.markdown(f'<div class="side-brand">Bauer<span>Vest</span></div>'
                f'<div class="side-sub">Build your scenario — everything updates live.</div>',
                unsafe_allow_html=True)

    section("PORTFOLIO")
    cols = st.columns(3)
    raw = [cols[i].text_input(f"Stock {i + 1}", v, key=f"t{i}").strip().upper()
           for i, v in enumerate(["AAPL", "TGT", "KO"])]
    st.markdown(f'<div class="side-sub" style="margin-top:-4px">Always benchmarked against the '
                f'{BENCH_NAME} ({BENCH}).</div>', unsafe_allow_html=True)

    section("CONTRIBUTIONS")
    lump = float(st.number_input("Starting lump sum ($)", 0, 50_000_000, 1_000, step=500))
    monthly = float(st.number_input("Monthly contribution ($)", 0, 1_000_000, 200, step=25))
    start_year = st.slider("Look-back start year", 2000, TODAY.year - 1, 2015)
    reinvest = st.toggle("Reinvest dividends", True)

    section("CAREER")
    salary = float(st.number_input("Annual salary ($)", 0, 50_000_000, 65_000, step=1_000))
    raise_pct = st.slider("Yearly raise — contributions grow with it (%)", 0.0, 10.0, 3.0, 0.5) / 100
    use_match = st.toggle("Employer 401(k) match", True)
    match_pct = st.slider("Match rate (% of your contribution)", 0, 200, 50, 5, disabled=not use_match) / 100
    match_cap = st.slider("Matched up to (% of salary)", 0.0, 15.0, 6.0, 0.5, disabled=not use_match) / 100

# ───────────────────────────────────────────── load market data
tickers = list(dict.fromkeys([t for t in raw if t] + [BENCH]))
req_start = pd.Timestamp(f"{start_year}-01-01")
prices, problems = {}, []
with st.spinner("Pulling market data…"):
    for t in tickers:
        try:
            prices[t] = load_prices(t, (req_start - pd.DateOffset(days=10)).strftime("%Y-%m-%d"))
        except Exception as e:
            problems.append(f"**{t}** — {e}")
tickers = [t for t in tickers if t in prices]
if not tickers:
    st.error("Couldn't load any market data. Check your internet connection and ticker symbols.")
    st.stop()

common = max([req_start] + [prices[t].index[0] for t in tickers])
window = {t: prices[t][prices[t].index >= common] for t in tickers}
n_hist = max(len(w.index.to_period("M").unique()) for w in window.values())
you_h, emp_h = contributions(n_hist, monthly, salary, raise_pct, use_match, match_pct, match_cap)
results, irr, rk = {}, {}, {}
for t in tickers:
    results[t], irr[t] = backtest(window[t], lump, you_h, emp_h, reinvest)
    rk[t] = risk(window[t], reinvest)

# ───────────────────────────────────────────── sidebar · future inputs
with st.sidebar:
    section("LOOK AHEAD")
    a1, a2 = st.columns(2)
    age = int(a1.number_input("Your age", 16, 80, 22))
    retire = int(a2.number_input("Retire at", 30, 95, 65))
    delay = st.slider("Compare with starting … years later", 1, 25, 8)
    opts = {"Custom rate": None}
    for t in tickers:
        opts[f"{label_of(t)} historical · {pct(rk[t]['cagr'])}"] = rk[t]["cagr"]
    choice = st.selectbox("Expected annual return", list(opts))
    exp_r = opts[choice] if opts[choice] is not None else \
        st.slider("Custom annual return (%)", 0.0, 15.0, 8.0, 0.25) / 100
    real = st.toggle("Show in today's dollars (inflation-adjusted)", True)
    infl = st.slider("Inflation (%)", 0.0, 8.0, 3.0, 0.25, disabled=not real) / 100 if real else 0.0

    section("GOAL")
    goal = float(st.number_input("Target amount ($)", 10_000, 500_000_000, 1_000_000, step=50_000))
    goal_age = int(st.number_input("By age", 18, 100, 50))

if retire <= age:
    st.error("Retirement age needs to be after your current age.")
    st.stop()

# ───────────────────────────────────────────── projections
def deflate(values, month_offset):
    t = (np.arange(len(values)) + month_offset) / 12
    return values / (1 + infl) ** t if real else values


n_now = (retire - age) * 12
n_late = max((retire - age - delay) * 12, 0)
you_f, emp_f = contributions(n_now, monthly, salary, raise_pct, use_match, match_pct, match_cap)
path_now = deflate(grow(n_now, lump, you_f, emp_f, exp_r), 0)
path_late = deflate(grow(n_late, lump, you_f[:n_late], emp_f[:n_late], exp_r), delay * 12)
end_now, end_late = path_now[-1], path_late[-1]
cost_wait = end_now - end_late
put_now = lump + you_f.sum()
put_late = lump + you_f[:n_late].sum()

best = max((t for t in tickers if t != BENCH), key=lambda t: results[t]["value"].iloc[-1], default=BENCH)
bench_df = results[BENCH] if BENCH in results else None
invested_you = results[tickers[0]]["you"].iloc[-1]
invested_emp = results[tickers[0]]["emp"].iloc[-1]
dollars = "today's dollars" if real else "future dollars"

# ───────────────────────────────────────────── hero
link = f' · <a href="{html.escape(LINKEDIN_URL)}" target="_blank">LinkedIn ↗</a>' if LINKEDIN_URL else ""
st.markdown(f"""
<div class="hero">
<div class="eyebrow">INVESTMENT ANALYTICS STUDIO</div>
<div class="brand">Bauer<span>Vest</span></div>
<div class="tagline">{TAGLINE}</div>
<div class="byline">{AUTHOR_LINE}{link}</div>
</div>""", unsafe_allow_html=True)

WALKTHROUGH = Path(__file__).parent / "walkthrough.mp4"
if WALKTHROUGH.exists():
    st.markdown(f"""<style>
[data-testid="stExpander"] details {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 16px; }}
[data-testid="stExpander"] summary p {{ color: {GOLD}; font-weight: 600; letter-spacing: .02em; }}
</style>""", unsafe_allow_html=True)
    with st.expander("New here? Watch the 2-minute walkthrough"):
        st.video(str(WALKTHROUGH), start_time=3)
        st.caption("Tour of every feature. The video uses sample data; the app above uses live market data.")

st.markdown('<div class="kpi-row">' + "".join([
    kpi("You invested", big(invested_you), f"+ {big(invested_emp)} employer match since {common:%b %Y}", SILVER),
    kpi("Top performer", big(results[best]["value"].iloc[-1]), f"{label_of(best)} · {pct(irr[best])}/yr", GOLD),
    kpi(f"{BENCH_NAME} portfolio", big(bench_df["value"].iloc[-1]) if bench_df is not None else "—",
        f"{pct(irr.get(BENCH))}/yr money-weighted", VIOLET),
    kpi("Cost of waiting", big(cost_wait), f"starting {delay} yrs late · {dollars}", ROSE),
]) + "</div>", unsafe_allow_html=True)

for p in problems:
    st.warning(p)
if common > req_start + pd.Timedelta(days=15):
    st.info(f"Look-back starts {common:%b %Y} — the first month every selected ticker has price history.")

tab_back, tab_ahead, tab_goal, tab_mc, tab_health, tab_risk, tab_method = st.tabs(
    ["↺  Look Back", "↗  Look Ahead", "◎  Goal Planner", "⚄  Monte Carlo", "✚  Health Check", "≋  Risk Lens",
     "ⓘ  Methodology"])

# ───────────────────────────────────────────── look back
with tab_back:
    st.markdown(f'<div class="insight">Investing <b>{money(monthly)}/month</b>'
                f'{f" plus a {money(lump)} lump sum" if lump else ""} since <b>{common:%B %Y}</b>, '
                f'the best result came from <b>{label_of(best)}</b>: '
                f'<b>{money(results[best]["value"].iloc[-1])}</b> from '
                f'{money(invested_you + invested_emp)} contributed.</div>', unsafe_allow_html=True)
    fig = go.Figure()
    base = results[tickers[0]]
    fig.add_trace(go.Scatter(x=base.index, y=base["you"] + base["emp"], name="Total contributed",
                             line=dict(color=MUTED, width=1.5, dash="dot"),
                             fill="tozeroy", fillcolor="rgba(142,139,163,0.08)"))
    for t in tickers:
        fig.add_trace(go.Scatter(x=results[t].index, y=results[t]["value"], name=label_of(t),
                                 line=dict(color=color_of(t, tickers), width=3 if t != BENCH else 2,
                                           dash="dash" if t == BENCH else None)))
    show_chart(style(fig, 460))

    rows = "".join(
        f'<tr><td><span class="dot" style="background:{color_of(t, tickers)}"></span>{label_of(t)}</td>'
        f'<td>{money(results[t]["value"].iloc[-1])}</td>'
        f'<td>{money(results[t]["you"].iloc[-1])}</td><td>{money(results[t]["emp"].iloc[-1])}</td>'
        f'<td>{money(results[t]["value"].iloc[-1] - results[t]["you"].iloc[-1] - results[t]["emp"].iloc[-1])}</td>'
        f'<td>{pct(irr[t])}</td><td>{pct(rk[t]["cagr"])}</td></tr>' for t in tickers)
    st.markdown(f'<div class="panel"><table class="tbl"><tr><th>Investment</th><th>Value today</th>'
                f'<th>You put in</th><th>Employer match</th><th>Market gain</th>'
                f'<th>Your return (IRR)</th><th>Stock CAGR</th></tr>{rows}</table></div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="note">IRR is the money-weighted return on every dollar you and your employer '
                f'put in, at the dates you put it in. Stock CAGR is the investment\'s own annual growth '
                f'{"with" if reinvest else "without"} dividends reinvested.</div>', unsafe_allow_html=True)

# ───────────────────────────────────────────── look ahead
with tab_ahead:
    st.markdown(f'<div class="insight">Starting at <b>{age}</b> grows to <b>{money(end_now)}</b> by {retire}. '
                f'Waiting until <b>{age + delay}</b> lands at <b>{money(end_late)}</b>. Waiting saves you '
                f'{money(put_now - put_late)} in contributions but costs <b>{money(cost_wait)}</b> in '
                f'{dollars}: about <b>{money(cost_wait / delay)}</b> for every year you wait.</div>',
                unsafe_allow_html=True)
    ages_now = age + np.arange(n_now + 1) / 12
    ages_late = age + delay + np.arange(n_late + 1) / 12
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages_now, y=path_now, name=f"Start at {age}",
                             line=dict(color=GOLD, width=3), fill="tozeroy",
                             fillcolor="rgba(232,194,122,0.10)"))
    fig.add_trace(go.Scatter(x=ages_late, y=path_late, name=f"Start at {age + delay}",
                             line=dict(color=VIOLET, width=3), fill="tozeroy",
                             fillcolor="rgba(160,143,255,0.10)"))
    fig.add_annotation(x=retire, y=end_now, text=big(end_now), showarrow=False, xanchor="right",
                       yshift=16, font=dict(color=GOLD, size=15))
    fig.add_annotation(x=retire, y=end_late, text=big(end_late), showarrow=False, xanchor="right",
                       yshift=-16, font=dict(color=VIOLET, size=15))
    style(fig, 460)
    fig.update_xaxes(title="Age", title_font=dict(color=MUTED))
    fig.update_layout(hovermode="x")
    show_chart(fig)

    c1, c2 = st.columns(2)
    for col, label, n, end, color in [(c1, f"Start at {age}", n_now, end_now, GOLD),
                                      (c2, f"Start at {age + delay}", n_late, end_late, VIOLET)]:
        y_sum, e_sum = lump + you_f[:n].sum(), emp_f[:n].sum()
        nominal_end = grow(n, lump, you_f[:n], emp_f[:n], exp_r)[-1]
        growth_part = nominal_end - y_sum - e_sum
        bar = go.Figure()
        for name, val, c in [("You", y_sum, SILVER), ("Employer", e_sum, TEAL), ("Market growth", growth_part, color)]:
            bar.add_trace(go.Bar(y=[""], x=[val], name=name, orientation="h", marker_color=c,
                                 hovertemplate=f"{name}: %{{x:$,.0f}}<extra></extra>"))
        style(bar, 140)
        bar.update_layout(barmode="stack", margin=dict(l=4, r=4, t=34, b=4), hovermode="closest",
                          legend=dict(traceorder="normal"))
        bar.update_yaxes(showticklabels=False)
        bar.update_xaxes(tickprefix="$", tickformat="~s")
        with col:
            st.markdown(f'<div class="panel" style="padding:12px 18px;margin-bottom:0"><h4>{label}</h4>'
                        f'<div class="note">Where the {money(nominal_end)} (future dollars) comes from</div></div>',
                        unsafe_allow_html=True)
            show_chart(bar)

# ───────────────────────────────────────────── goal planner
with tab_goal:
    if goal_age <= age:
        st.warning("Set a goal age later than your current age.")
    else:
        n_goal = (goal_age - age) * 12
        target_nominal = goal * (1 + infl) ** (goal_age - age)

        def fv(m):
            y, e = contributions(n_goal, m, salary, raise_pct, use_match, match_pct, match_cap)
            return grow(n_goal, lump, y, e, exp_r)[-1]

        if fv(0) >= target_nominal:
            need = 0.0
        else:
            lo, hi = 0.0, 1_000.0
            while fv(hi) < target_nominal and hi < 1e9:
                hi *= 2
            for _ in range(80):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if fv(mid) < target_nominal else (lo, mid)
            need = hi
        on_plan = fv(monthly)
        gap = on_plan - target_nominal
        status = (f'<b style="color:{GREEN}">On track</b>: your current {money(monthly)}/month gets you '
                  f'{money(on_plan / (1 + infl) ** (goal_age - age))} ({dollars}).' if gap >= 0 else
                  f'<b style="color:{ROSE}">Short</b>: your current {money(monthly)}/month reaches '
                  f'{money(on_plan / (1 + infl) ** (goal_age - age))} ({dollars}).')
        g1, g2, g3 = st.columns(3)
        g1.markdown(kpi("Needed per month", money(need), f"starting now, growing {pct(raise_pct)}/yr", GOLD),
                    unsafe_allow_html=True)
        g2.markdown(kpi("Goal", big(goal), f"by age {goal_age} · {dollars}", VIOLET), unsafe_allow_html=True)
        g3.markdown(kpi("Years to goal", f"{goal_age - age}", f"at {pct(exp_r)} expected return", TEAL),
                    unsafe_allow_html=True)
        st.markdown(f'<div class="insight">{status} Employer match is included. '
                    f'{"The goal is shown in today’s dollars; the future-dollar target is " + money(target_nominal) + "." if real else ""}'
                    f'</div>', unsafe_allow_html=True)

        y_need, e_need = contributions(n_goal, need, salary, raise_pct, use_match, match_pct, match_cap)
        y_cur, e_cur = contributions(n_goal, monthly, salary, raise_pct, use_match, match_pct, match_cap)
        ages = age + np.arange(n_goal + 1) / 12
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ages, y=deflate(grow(n_goal, lump, y_need, e_need, exp_r), 0),
                                 name=f"Goal plan · {money(need)}/mo", line=dict(color=GOLD, width=3)))
        fig.add_trace(go.Scatter(x=ages, y=deflate(grow(n_goal, lump, y_cur, e_cur, exp_r), 0),
                                 name=f"Current plan · {money(monthly)}/mo", line=dict(color=VIOLET, width=3, dash="dash")))
        fig.add_hline(y=goal, line=dict(color=ROSE, width=1.5, dash="dot"),
                      annotation_text=f"Goal {big(goal)}", annotation_font_color=ROSE,
                      annotation_position="top left")
        style(fig, 440)
        fig.update_xaxes(title="Age", title_font=dict(color=MUTED))
        show_chart(fig)

# ───────────────────────────────────────────── monte carlo
with tab_mc:
    bench_vol = rk[BENCH]["vol"] if BENCH in rk else 0.16
    m1, m2 = st.columns([2, 1])
    vol = m1.slider(f"Annual volatility (%) · {BENCH_NAME} historical: {pct(bench_vol)}", 2.0, 60.0,
                    float(np.clip(round(bench_vol * 100), 2, 60)), 0.5) / 100
    sims = m2.selectbox("Simulated markets", [500, 1_000, 2_000, 5_000], index=2)

    n_sim = max(n_now, (goal_age - age) * 12 if goal_age > age else 0)
    you_s, emp_s = contributions(n_sim, monthly, salary, raise_pct, use_match, match_pct, match_cap)
    paths = monte_carlo(n_sim, lump, you_s, emp_s, exp_r, vol, sims)
    if real:
        paths = paths / (1 + infl) ** (np.arange(n_sim + 1) / 12)
    at_retire = paths[:, n_now]
    p10, p50, p90 = np.percentile(at_retire, [10, 50, 90])
    goal_ok = goal_age > age
    hit = float(np.mean(paths[:, (goal_age - age) * 12] >= goal)) if goal_ok else np.nan
    p_loss = float(np.mean(at_retire < lump + you_s[:n_now].sum()))

    st.markdown(f'<div class="kpi-row">' + "".join([
        kpi("Chance of hitting goal", pct(hit, 0) if goal_ok else "—",
            f"{big(goal)} by {goal_age} · current plan" if goal_ok else "set a goal age", GOLD),
        kpi("Median at retirement", big(p50), f"age {retire} · {dollars}", VIOLET),
        kpi("Bad-luck market", big(p10), "10th percentile outcome", ROSE),
        kpi("Good-luck market", big(p90), "90th percentile outcome", TEAL),
    ]) + "</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="insight">Across <b>{sims:,}</b> simulated markets averaging <b>{pct(exp_r)}</b> a year '
                f'with <b>{pct(vol)}</b> volatility, your plan ends between <b>{money(p10)}</b> and '
                f'<b>{money(p90)}</b> in 8 out of 10 outcomes'
                f'{f", and hits your {big(goal)} goal <b>{pct(hit, 0)}</b> of the time" if goal_ok else ""}. '
                f'The same average return can produce very different results depending on the order of good '
                f'and bad years.</div>', unsafe_allow_html=True)

    ages_sim = age + np.arange(n_now + 1) / 12
    q = np.percentile(paths[:, :n_now + 1], [10, 25, 50, 75, 90], axis=0)
    fig = go.Figure()
    for hi, lo, alpha, name in [(4, 0, .10, "10th–90th percentile"), (3, 1, .22, "25th–75th percentile")]:
        fig.add_trace(go.Scatter(x=ages_sim, y=q[hi], line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=ages_sim, y=q[lo], line=dict(width=0), fill="tonexty",
                                 fillcolor=f"rgba(160,143,255,{alpha})", name=name, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ages_sim, y=q[2], name="Median outcome", line=dict(color=GOLD, width=3)))
    fig.add_trace(go.Scatter(x=ages_sim, y=path_now, name="Look Ahead projection",
                             line=dict(color=SILVER, width=1.5, dash="dot")))
    if goal_ok and goal_age <= retire:
        fig.add_trace(go.Scatter(x=[goal_age], y=[goal], mode="markers+text", name="Your goal",
                                 marker=dict(color=ROSE, size=12, symbol="diamond"),
                                 text=[f"Goal {big(goal)}"], textposition="top center",
                                 textfont=dict(color=ROSE)))
    style(fig, 460)
    fig.update_xaxes(title="Age", title_font=dict(color=MUTED))
    show_chart(fig)

    cap = np.percentile(at_retire, 99)
    hist = go.Figure(go.Histogram(x=np.clip(at_retire, None, cap), nbinsx=60, marker_color=VIOLET,
                                  marker_line=dict(color=BG, width=1), name="Outcomes",
                                  hovertemplate="%{x:$,.0f}: %{y} markets<extra></extra>"))
    for val, label, c, side in [(p10, "10th", ROSE, "top left"), (p50, "Median", GOLD, "top right"),
                                (p90, "90th", TEAL, "top right")]:
        hist.add_vline(x=val, line=dict(color=c, width=2, dash="dash"),
                       annotation_text=f"{label} {big(val)}", annotation_font_color=c,
                       annotation_position=side)
    style(hist, 340, money_axis=False)
    hist.update_xaxes(tickprefix="$", tickformat="~s", title=f"Balance at {retire} ({dollars})",
                      title_font=dict(color=MUTED))
    hist.update_yaxes(title="Simulated markets", title_font=dict(color=MUTED))
    hist.update_layout(showlegend=False, hovermode="closest", bargap=.05)
    st.markdown('<div class="panel" style="padding:12px 18px;margin-bottom:0"><h4>Distribution at retirement</h4>'
                f'<div class="note">Each bar counts how many simulated markets ended in that range. '
                f'In {pct(p_loss, 1)} of markets you finish with less than you contributed.</div></div>',
                unsafe_allow_html=True)
    show_chart(hist)

# ───────────────────────────────────────────── health check
with tab_health:
    st.markdown('<div class="note" style="margin-bottom:14px">Report cards built from each company\'s latest '
                'annual 10-K filing with the SEC (XBRL financial data). Grades use general rules of thumb; '
                'healthy levels differ by industry (retailers, for example, run low current ratios by design).</div>',
                unsafe_allow_html=True)
    firms = [t for t in tickers if t != BENCH]
    if not firms:
        st.info("Add at least one individual stock to see its health check.")
    else:
        cols = st.columns(len(firms))
        for col, t in zip(cols, firms):
            with col:
                try:
                    hc = health_check(t)
                except Exception:
                    hc = "error"
                if hc in (None, "error"):
                    msg = ("SEC data unavailable right now." if hc == "error"
                           else "No SEC financials (likely a fund or foreign listing).")
                    st.markdown(f'<div class="hc"><div class="hc-tic">{html.escape(t)}</div>'
                                f'<div class="note" style="margin-top:10px">{msg}</div></div>',
                                unsafe_allow_html=True)
                    continue
                oc = GRADE_COLOR[hc["overall"]]
                rows = "".join(
                    f'<div class="hc-row"><div><div class="hc-k">{m[1]}</div><div class="hc-x">{m[4]}</div></div>'
                    f'<div style="display:flex;align-items:center"><span class="hc-v">{m[2]}</span>'
                    f'<span class="pill" style="color:{GRADE_COLOR[m[3]]};background:{GRADE_COLOR[m[3]]}1F">{m[3]}</span></div></div>'
                    for m in hc["metrics"])
                st.markdown(
                    f'<div class="hc"><div class="hc-top"><div><div class="hc-tic">{html.escape(t)}</div>'
                    f'<div class="hc-name">{html.escape(hc["name"])} · FY ending {hc["fy"]:%b %Y}</div></div>'
                    f'<div style="text-align:right"><div class="hc-grade" style="color:{oc}">{hc["overall"]}</div>'
                    f'<div class="hc-x">GPA {hc["gpa"]:.1f} / 4.0</div></div></div>'
                    f'<div style="margin-top:12px">{rows}</div></div>', unsafe_allow_html=True)

# ───────────────────────────────────────────── risk lens
with tab_risk:
    lowest_dd = min(tickers, key=lambda t: rk[t]["maxdd"])
    st.markdown(f'<div class="insight">Higher returns usually come with bigger swings. The deepest drop in this '
                f'window was <b>{label_of(lowest_dd)}</b> at <b>{pct(rk[lowest_dd]["maxdd"])}</b> from its peak. '
                f'Diversified index funds tend to fall less than single stocks.</div>', unsafe_allow_html=True)
    rows = "".join(
        f'<tr><td><span class="dot" style="background:{color_of(t, tickers)}"></span>{label_of(t)}</td>'
        f'<td>{pct(rk[t]["cagr"])}</td><td>{pct(rk[t]["vol"])}</td>'
        f'<td style="color:{RED}">{pct(rk[t]["maxdd"])}</td>'
        f'<td style="color:{GREEN}">{pct(rk[t]["yearly"].max())} ({rk[t]["yearly"].idxmax()})</td>'
        f'<td style="color:{RED}">{pct(rk[t]["yearly"].min())} ({rk[t]["yearly"].idxmin()})</td>'
        f'<td>{rk[t]["cagr"] / rk[t]["vol"]:.2f}</td></tr>' for t in tickers)
    st.markdown(f'<div class="panel"><table class="tbl"><tr><th>Investment</th><th>CAGR</th>'
                f'<th>Volatility</th><th>Max drawdown</th><th>Best year</th><th>Worst year</th>'
                f'<th>Return / risk</th></tr>{rows}</table></div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="panel" style="padding:12px 18px;margin-bottom:0"><h4>Drawdown from peak</h4></div>',
                    unsafe_allow_html=True)
        fig = go.Figure()
        for t in tickers:
            dd = rk[t]["dd"].resample("W").min()
            fig.add_trace(go.Scatter(x=dd.index, y=dd, name=label_of(t),
                                     line=dict(color=color_of(t, tickers), width=1.6)))
        style(fig, 380, money_axis=False)
        fig.update_yaxes(tickformat=".0%")
        show_chart(fig)
    with r2:
        st.markdown('<div class="panel" style="padding:12px 18px;margin-bottom:0"><h4>Calendar-year returns</h4></div>',
                    unsafe_allow_html=True)
        fig = go.Figure()
        for t in tickers:
            y = rk[t]["yearly"]
            fig.add_trace(go.Bar(x=y.index.astype(str), y=y.values, name=label_of(t),
                                 marker_color=color_of(t, tickers)))
        style(fig, 380, money_axis=False)
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(barmode="group", bargap=.25, hovermode="x unified")
        show_chart(fig)

# ───────────────────────────────────────────── methodology
with tab_method:
    st.markdown(f"""
<div class="panel"><h4>How BauerVest works</h4>
<div class="note">
<b>Look Back.</b> Each month you (and your employer) buy shares at that month's first trading-day price.
Dividends {"are reinvested at month-end" if reinvest else "are held as cash"}. Contributions rise once a year with your raise.
Your return is the money-weighted <b>IRR</b> of every contribution against today's value. Stock CAGR uses a total-return
index: (Price<sub>t</sub> + Dividend<sub>t</sub>) ÷ Price<sub>t−1</sub>.<br><br>
<b>Employer match.</b> Monthly match = match rate × min(your contribution, cap % × salary ÷ 12).<br><br>
<b>Look Ahead.</b> Balance<sub>m+1</sub> = (Balance<sub>m</sub> + contributions) × (1 + r)<sup>1/12</sup>.
In today's dollars, values are divided by (1 + inflation)<sup>years</sup>. The later starter follows the same plan, shifted.<br><br>
<b>Goal Planner.</b> Solves for the monthly contribution whose future value equals the goal (bisection), including match and raises.<br><br>
<b>Monte Carlo.</b> Simulates thousands of possible markets. Each month's return is drawn at random:
growth = e<sup>Z</sup>, with Z ~ Normal(ln(1 + r) ÷ 12, volatility ÷ √12), so the median market grows at the expected return
while individual paths swing above and below it. Percentiles across all paths give the outcome ranges and the probability of reaching the goal.<br><br>
<b>Health Check.</b> Latest annual 10-K values from SEC EDGAR XBRL: current ratio = current assets ÷ current liabilities;
net margin = net income ÷ revenue; ROE = net income ÷ shareholders' equity; debt-to-equity = total debt ÷ equity;
revenue growth = 3-year CAGR. Letter grades are averaged on a 4.0 scale.<br><br>
<b>Risk Lens.</b> Volatility = standard deviation of monthly returns × √12. Max drawdown = largest peak-to-trough drop.
Return / risk = CAGR ÷ volatility.<br><br>
<b>Data.</b> Prices and dividends: Yahoo Finance (via yfinance). Fundamentals: SEC EDGAR. Built with Python, pandas, Plotly and Streamlit.
</div></div>""", unsafe_allow_html=True)

st.markdown(f'<div class="foot">{APP_NAME} · {AUTHOR_LINE} · For educational purposes only, not investment advice. '
            f'Past performance does not guarantee future results.</div>', unsafe_allow_html=True)
