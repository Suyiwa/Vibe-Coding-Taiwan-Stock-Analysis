# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║         🔍 股票分析系統 v2.0                         ║
║         Stock Analysis System - Powered by Yahoo Finance  ║
╚══════════════════════════════════════════════════════════╝
#2330.TW,2454.TW,0050.TW  9988.HK,0700.HK
使用方式：
    1. 安裝套件：pip install yfinance mplfinance matplotlib pandas numpy
    2. 執行後輸入股票代碼（台股請加 .TW，例如 2330.TW）
    3. 可同時輸入多檔，以逗號分隔
"""
 
# ─────────────────────────────────────────────
# 📦 套件安裝（Colab 環境使用）
# ─────────────────────────────────────────────
#pip install yfinance mplfinance matplotlib pandas numpy
 
# ─────────────────────────────────────────────
# 📚 Import
# ─────────────────────────────────────────────
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import mplfinance as mpf
import warnings
warnings.filterwarnings("ignore")
 
# ─────────────────────────────────────────────
# 🎨 全域樣式設定
# ─────────────────────────────────────────────
plt.rcParams.update({
    'font.family': ['Microsoft JhengHei', 'DejaVu Sans'],  # 支援中文（Windows/Linux）
    'axes.facecolor': '#1a1a2e',
    'figure.facecolor': '#0f0f1a',
    'axes.edgecolor': '#444466',
    'axes.labelcolor': '#ccccee',
    'xtick.color': '#aaaacc',
    'ytick.color': '#aaaacc',
    'text.color': '#eeeeff',
    'grid.color': '#2a2a4a',
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
    'legend.facecolor': '#1a1a2e',
    'legend.edgecolor': '#444466',
})
 
COLORS = {
    'price':    '#00d4ff',
    'ma5':      '#ffd700',
    'ma20':     '#ff6b6b',
    'ma60':     '#a29bfe',
    'volume_up':   '#26a69a',
    'volume_dn':   '#ef5350',
    'rsi':      '#f39c12',
    'macd':     '#00cec9',
    'signal':   '#fd79a8',
    'hist_pos': '#26a69a',
    'hist_neg': '#ef5350',
    'bb_upper': '#636e72',
    'bb_lower': '#636e72',
    'bb_mid':   '#b2bec3',
}
 
# ═══════════════════════════════════════════════════════════
# 📐 技術指標計算函數
# ═══════════════════════════════════════════════════════════
 
def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """計算 RSI（相對強弱指數）"""
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
 
def calculate_macd(data: pd.DataFrame, fast=12, slow=26, signal=9):
    """計算 MACD 指標"""
    ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram
 
def calculate_bollinger_bands(data: pd.DataFrame, window=20, num_std=2):
    """計算布林通道（Bollinger Bands）"""
    ma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return upper, ma, lower
 
def calculate_stochastic(data: pd.DataFrame, k_period=14, d_period=3):
    """計算 KD 指標（隨機震盪）"""
    low_min = data['Low'].rolling(k_period).min()
    high_max = data['High'].rolling(k_period).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    return k, d
 
def calculate_atr(data: pd.DataFrame, window=14) -> pd.Series:
    """計算 ATR（平均真實範圍，波動度）"""
    high_low = data['High'] - data['Low']
    high_close = (data['High'] - data['Close'].shift()).abs()
    low_close = (data['Low'] - data['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()
 
# ═══════════════════════════════════════════════════════════
# 📊 資料抓取與整理
# ═══════════════════════════════════════════════════════════
 
def fetch_stock_data(stock_code: str, period: str = "6mo") -> tuple:
    """
    抓取股票資料（技術 + 基本面）
    回傳: (df, info_dict) 或 (None, None) 若失敗
    """
    try:
        ticker = yf.Ticker(stock_code)
        df = ticker.history(period=period)
 
        if df.empty:
            print(f"  ⚠️  找不到 {stock_code} 的資料，請確認股票代碼")
            return None, None
 
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)  # 移除時區
 
        # ── 技術指標 ──
        df['MA5']  = df['Close'].rolling(5).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA60'] = df['Close'].rolling(60).mean()
        df['RSI']  = calculate_rsi(df)
        df['MACD'], df['Signal'], df['Hist'] = calculate_macd(df)
        df['BB_Upper'], df['BB_Mid'], df['BB_Lower'] = calculate_bollinger_bands(df)
        df['K'], df['D'] = calculate_stochastic(df)
        df['ATR'] = calculate_atr(df)
 
        # ── 基本面 ──
        raw_info = ticker.info
        info = {
            'name':              raw_info.get('longName') or raw_info.get('shortName', stock_code),
            'sector':            raw_info.get('sector', 'N/A'),
            'industry':          raw_info.get('industry', 'N/A'),
            'currency':          raw_info.get('currency', ''),
            'current_price':     raw_info.get('currentPrice') or df['Close'].iloc[-1],
            'market_cap':        raw_info.get('marketCap'),
            'pe_ratio':          raw_info.get('trailingPE'),
            'forward_pe':        raw_info.get('forwardPE'),
            'eps':               raw_info.get('trailingEps'),
            'dividend_yield':    raw_info.get('dividendYield'),
            'week52_high':       raw_info.get('fiftyTwoWeekHigh'),
            'week52_low':        raw_info.get('fiftyTwoWeekLow'),
            'avg_volume':        raw_info.get('averageVolume'),
            'beta':              raw_info.get('beta'),
            'roe':               raw_info.get('returnOnEquity'),
            'debt_to_equity':    raw_info.get('debtToEquity'),
            'revenue_growth':    raw_info.get('revenueGrowth'),
        }
 
        return df, info
 
    except Exception as e:
        print(f"  ❌ 抓取 {stock_code} 時發生錯誤：{e}")
        return None, None
 
# ═══════════════════════════════════════════════════════════
# 🧠 多維度評分系統
# ═══════════════════════════════════════════════════════════
 
def analyze_stock(df: pd.DataFrame, info: dict) -> dict:
    """
    多維度加權評分（技術面 + 基本面）
    每項指標：+1（正向）/ 0（中性）/ -1（負向）
    """
    latest  = df.iloc[-1]
    prev    = df.iloc[-2]
    signals = []
    score   = 0
 
    # ══ 技術面 ══
 
    # 1. 趨勢（MA交叉）
    if latest['MA5'] > latest['MA20']:
        score += 1
        signals.append(('✅', '短期趨勢向上', 'MA5 > MA20'))
    else:
        score -= 1
        signals.append(('❌', '短期趨勢向下', 'MA5 < MA20'))
 
    # 2. 長期趨勢
    if not pd.isna(latest['MA60']):
        if latest['Close'] > latest['MA60']:
            score += 1
            signals.append(('✅', '長期趨勢偏多', f"收盤價 {latest['Close']:.1f} > MA60 {latest['MA60']:.1f}"))
        else:
            score -= 1
            signals.append(('❌', '長期趨勢偏空', f"收盤價 {latest['Close']:.1f} < MA60 {latest['MA60']:.1f}"))
 
    # 3. RSI 超買超賣
    rsi = latest['RSI']
    if 40 <= rsi <= 65:
        score += 1
        signals.append(('✅', 'RSI 區間健康', f"RSI = {rsi:.1f}（理想區間 40~65）"))
    elif rsi < 30:
        score += 1  # 超賣，可能反彈
        signals.append(('⚠️', 'RSI 超賣，留意反彈', f"RSI = {rsi:.1f} < 30"))
    elif rsi > 70:
        score -= 1
        signals.append(('❌', 'RSI 過熱，注意回調', f"RSI = {rsi:.1f} > 70"))
    else:
        signals.append(('➖', 'RSI 中性', f"RSI = {rsi:.1f}"))
 
    # 4. MACD 黃金/死亡交叉
    if latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal']:
        score += 2  # 黃金交叉，強烈信號
        signals.append(('🌟', 'MACD 黃金交叉', '動能剛轉強（強烈買進信號）'))
    elif latest['MACD'] < latest['Signal'] and prev['MACD'] >= prev['Signal']:
        score -= 2
        signals.append(('💀', 'MACD 死亡交叉', '動能剛轉弱（強烈賣出信號）'))
    elif latest['MACD'] > latest['Signal']:
        score += 1
        signals.append(('✅', 'MACD 動能向上', f"MACD {latest['MACD']:.3f} > Signal {latest['Signal']:.3f}"))
    else:
        score -= 1
        signals.append(('❌', 'MACD 動能向下', f"MACD {latest['MACD']:.3f} < Signal {latest['Signal']:.3f}"))
 
    # 5. 布林通道位置
    bb_pct = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
    if bb_pct < 0.2:
        score += 1
        signals.append(('✅', '布林通道下緣支撐', f"BB%B = {bb_pct:.2f}，偏低有撐"))
    elif bb_pct > 0.8:
        score -= 1
        signals.append(('❌', '布林通道上緣壓力', f"BB%B = {bb_pct:.2f}，偏高有壓"))
    else:
        signals.append(('➖', '布林通道中段', f"BB%B = {bb_pct:.2f}"))
 
    # 6. KD 指標
    k, d = latest['K'], latest['D']
    if k > d and k < 80:
        score += 1
        signals.append(('✅', 'KD 黃金排列', f"K={k:.1f} > D={d:.1f}，動能佳"))
    elif k < d and k > 20:
        score -= 1
        signals.append(('❌', 'KD 死亡排列', f"K={k:.1f} < D={d:.1f}，動能弱"))
    elif k < 20:
        score += 1
        signals.append(('⚠️', 'KD 超賣區', f"K={k:.1f}，留意超跌反彈"))
    elif k > 80:
        score -= 1
        signals.append(('❌', 'KD 超買區', f"K={k:.1f}，留意獲利了結"))
    else:
        signals.append(('➖', 'KD 中性', f"K={k:.1f}, D={d:.1f}"))
 
    # 7. 成交量
    recent_vol = df['Volume'].tail(5).mean()
    avg_vol    = info.get('avg_volume') or df['Volume'].mean()
    if avg_vol and avg_vol > 0:
        vol_ratio = recent_vol / avg_vol
        if vol_ratio > 1.3:
            score += 1
            signals.append(('✅', '成交量放大', f"近5日均量 {vol_ratio:.1f}x 於長期均量"))
        elif vol_ratio < 0.7:
            signals.append(('⚠️', '成交量萎縮', f"近5日均量僅長期均量的 {vol_ratio:.1f}x"))
        else:
            signals.append(('➖', '成交量正常', f"量比 {vol_ratio:.1f}x"))
 
    # ══ 基本面 ══
 
    # 8. 本益比
    pe = info.get('pe_ratio')
    if pe:
        if pe < 15:
            score += 1
            signals.append(('✅', '本益比偏低（相對便宜）', f"PE = {pe:.1f}x"))
        elif pe > 35:
            score -= 1
            signals.append(('❌', '本益比偏高（相對貴）', f"PE = {pe:.1f}x"))
        else:
            signals.append(('➖', '本益比合理', f"PE = {pe:.1f}x"))
 
    # 9. 股息殖利率
    div = info.get('dividend_yield')
    if div:
        pct = div * 100
        if pct >= 3:
            score += 1
            signals.append(('✅', '股息殖利率佳', f"殖利率 = {pct:.1f}%"))
        else:
            signals.append(('➖', '股息殖利率普通', f"殖利率 = {pct:.1f}%"))
 
    # 10. 52週高低位置
    w52h = info.get('week52_high')
    w52l = info.get('week52_low')
    price = latest['Close']
    if w52h and w52l and (w52h - w52l) > 0:
        pos_pct = (price - w52l) / (w52h - w52l) * 100
        if pos_pct < 30:
            score += 1
            signals.append(('✅', '接近52週低點（低買機會）', f"位於52週區間 {pos_pct:.0f}% 位置"))
        elif pos_pct > 80:
            score -= 1
            signals.append(('❌', '接近52週高點（高位風險）', f"位於52週區間 {pos_pct:.0f}% 位置"))
        else:
            signals.append(('➖', '52週區間中段', f"位於 {pos_pct:.0f}% 位置"))
 
    # ── 最終評級 ──
    max_score = 12
    if score >= 6:
        verdict = '強力買進 🚀'
        verdict_color = '#00ff88'
    elif score >= 3:
        verdict = '建議買進 📈'
        verdict_color = '#26a69a'
    elif score >= 0:
        verdict = '中性觀望 ⏸️'
        verdict_color = '#f39c12'
    elif score >= -3:
        verdict = '建議減碼 📉'
        verdict_color = '#ef5350'
    else:
        verdict = '強力賣出 🔻'
        verdict_color = '#ff0055'
 
    return {
        'score':         score,
        'max_score':     max_score,
        'signals':       signals,
        'verdict':       verdict,
        'verdict_color': verdict_color,
    }
 
# ═══════════════════════════════════════════════════════════
# 🖨️ 文字報告輸出
# ═══════════════════════════════════════════════════════════
 
def _fmt_number(val, unit='', decimals=2):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 'N/A'
    if abs(val) >= 1e12:
        return f"{val/1e12:.1f}T{unit}"
    if abs(val) >= 1e8:
        return f"{val/1e8:.1f}億{unit}"
    if abs(val) >= 1e4:
        return f"{val/1e4:.1f}萬{unit}"
    return f"{val:.{decimals}f}{unit}"
 
def print_report(stock_code: str, df: pd.DataFrame, info: dict, result: dict):
    latest = df.iloc[-1]
    cur    = info.get('currency', '')
    score  = result['score']
 
    LINE  = "═" * 60
    DLINE = "─" * 60
 
    print(f"\n{LINE}")
    print(f"  📊 {info['name']}  ({stock_code})")
    print(f"  🏭 {info['sector']} | {info['industry']}")
    print(LINE)
 
    # 價格資訊
    print(f"\n  💰 最新收盤價：{latest['Close']:.2f} {cur}")
    w52h = info.get('week52_high')
    w52l = info.get('week52_low')
    if w52h and w52l:
        print(f"  📅 52週高低：{w52l:.1f} ─ {w52h:.1f} {cur}")
 
    # 基本面摘要
    print(f"\n  📋 基本面摘要")
    print(DLINE)
    pe  = info.get('pe_ratio')
    fpe = info.get('forward_pe')
    eps = info.get('eps')
    div = info.get('dividend_yield')
    mc  = info.get('market_cap')
    beta= info.get('beta')
    roe = info.get('roe')
    dte = info.get('debt_to_equity')
 
    print(f"  {'本益比 (trailing PE)':<22} {_fmt_number(pe, 'x') if pe else 'N/A'}")
    print(f"  {'預期本益比 (forward PE)':<22} {_fmt_number(fpe, 'x') if fpe else 'N/A'}")
    print(f"  {'每股盈餘 (EPS)':<22} {_fmt_number(eps)}")
    print(f"  {'股息殖利率':<22} {f'{div*100:.2f}%' if div else 'N/A'}")
    print(f"  {'市值':<22} {_fmt_number(mc)}")
    print(f"  {'Beta（市場波動比）':<22} {_fmt_number(beta)}")
    print(f"  {'ROE（股東權益報酬）':<22} {f'{roe*100:.1f}%' if roe else 'N/A'}")
    print(f"  {'負債/股東權益':<22} {_fmt_number(dte)}")
 
    # 技術面摘要
    print(f"\n  📈 技術指標（最新一日）")
    print(DLINE)
    print(f"  {'MA5 / MA20 / MA60':<22} {latest['MA5']:.1f} / {latest['MA20']:.1f} / {latest['MA60']:.1f}")
    print(f"  {'RSI (14)':<22} {latest['RSI']:.1f}")
    print(f"  {'MACD / Signal':<22} {latest['MACD']:.3f} / {latest['Signal']:.3f}")
    print(f"  {'K / D':<22} {latest['K']:.1f} / {latest['D']:.1f}")
    print(f"  {'ATR（平均真實波動）':<22} {latest['ATR']:.2f}")
 
    # 信號分析
    print(f"\n  🔍 信號分析（{len(result['signals'])} 項）")
    print(DLINE)
    for icon, label, detail in result['signals']:
        print(f"  {icon} {label:<20} │ {detail}")
 
    # 最終評分
    bar_filled = int((score + result['max_score']) / (result['max_score'] * 2) * 20)
    bar = '█' * bar_filled + '░' * (20 - bar_filled)
    print(f"\n{LINE}")
    print(f"  評分：{score:+d} / {result['max_score']}")
    print(f"  [{bar}]")
    print(f"  👉  {result['verdict']}")
    print(LINE)
 
# ═══════════════════════════════════════════════════════════
# 📉 圖表繪製（整合儀表板）
# ═══════════════════════════════════════════════════════════
 
def plot_dashboard(stock_code: str, df: pd.DataFrame, info: dict, result: dict):
    """繪製整合儀表板（一張圖包含所有指標）"""
 
    # 只取最近90天顯示
    plot_df = df.tail(90).copy()
    dates   = plot_df.index
 
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor('#0f0f1a')
 
    # 標題
    verdict = result['verdict']
    score   = result['score']
    name    = info.get('name', stock_code)
    currency= info.get('currency', '')
    price   = plot_df['Close'].iloc[-1]
 
    fig.suptitle(
        f"{name}  ({stock_code})    最新：{price:.2f} {currency}    "
        f"評分：{score:+d}    {verdict}",
        fontsize=14, fontweight='bold', color=result['verdict_color'],
        y=0.98
    )
 
    # GridSpec 佈局
    gs = gridspec.GridSpec(
        5, 1, figure=fig,
        height_ratios=[3, 1, 1, 1, 1],
        hspace=0.08
    )
 
    ax_price  = fig.add_subplot(gs[0])
    ax_vol    = fig.add_subplot(gs[1], sharex=ax_price)
    ax_rsi    = fig.add_subplot(gs[2], sharex=ax_price)
    ax_macd   = fig.add_subplot(gs[3], sharex=ax_price)
    ax_kd     = fig.add_subplot(gs[4], sharex=ax_price)
 
    # ── (1) 價格 + MA + 布林通道 ──
    ax_price.fill_between(dates, plot_df['BB_Upper'], plot_df['BB_Lower'],
                          alpha=0.08, color=COLORS['bb_upper'], label='布林通道')
    ax_price.plot(dates, plot_df['BB_Upper'], color=COLORS['bb_upper'], lw=0.8, ls='--')
    ax_price.plot(dates, plot_df['BB_Lower'], color=COLORS['bb_lower'], lw=0.8, ls='--')
    ax_price.plot(dates, plot_df['Close'],  color=COLORS['price'], lw=1.8, label='收盤價', zorder=5)
    ax_price.plot(dates, plot_df['MA5'],    color=COLORS['ma5'],   lw=1.2, label='MA5')
    ax_price.plot(dates, plot_df['MA20'],   color=COLORS['ma20'],  lw=1.2, label='MA20')
    if not plot_df['MA60'].isna().all():
        ax_price.plot(dates, plot_df['MA60'], color=COLORS['ma60'],  lw=1.2, label='MA60')
 
    # 標記最後收盤價
    ax_price.axhline(price, color=COLORS['price'], lw=0.5, ls=':', alpha=0.5)
    ax_price.text(dates[-1], price, f' {price:.1f}', color=COLORS['price'],
                  va='center', fontsize=9)
 
    ax_price.set_ylabel('價格', fontsize=10)
    ax_price.legend(loc='upper left', fontsize=9, framealpha=0.6, ncol=5)
    ax_price.grid(True)
 
    # ── (2) 成交量 ──
    colors_vol = [COLORS['volume_up'] if c >= o else COLORS['volume_dn']
                  for c, o in zip(plot_df['Close'], plot_df['Open'])]
    ax_vol.bar(dates, plot_df['Volume'], color=colors_vol, alpha=0.85, width=0.8)
    ax_vol.set_ylabel('成交量', fontsize=9)
    ax_vol.grid(True)
    ax_vol.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
 
    # ── (3) RSI ──
    ax_rsi.plot(dates, plot_df['RSI'], color=COLORS['rsi'], lw=1.5, label='RSI(14)')
    ax_rsi.axhline(70, color='#ef5350', lw=0.8, ls='--', alpha=0.7)
    ax_rsi.axhline(30, color='#26a69a', lw=0.8, ls='--', alpha=0.7)
    ax_rsi.axhline(50, color='#636e72', lw=0.5, ls=':', alpha=0.4)
    ax_rsi.fill_between(dates, 70, plot_df['RSI'].clip(upper=100),
                         where=plot_df['RSI'] > 70, alpha=0.15, color='#ef5350')
    ax_rsi.fill_between(dates, plot_df['RSI'].clip(lower=0), 30,
                         where=plot_df['RSI'] < 30, alpha=0.15, color='#26a69a')
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_ylabel('RSI', fontsize=9)
    ax_rsi.legend(loc='upper left', fontsize=8)
    ax_rsi.grid(True)
 
    # ── (4) MACD ──
    hist_colors = [COLORS['hist_pos'] if h >= 0 else COLORS['hist_neg']
                   for h in plot_df['Hist']]
    ax_macd.bar(dates, plot_df['Hist'], color=hist_colors, alpha=0.7, width=0.8, label='Histogram')
    ax_macd.plot(dates, plot_df['MACD'],   color=COLORS['macd'],   lw=1.4, label='MACD')
    ax_macd.plot(dates, plot_df['Signal'], color=COLORS['signal'], lw=1.2, label='Signal')
    ax_macd.axhline(0, color='#636e72', lw=0.6)
    ax_macd.set_ylabel('MACD', fontsize=9)
    ax_macd.legend(loc='upper left', fontsize=8, ncol=3)
    ax_macd.grid(True)
 
    # ── (5) KD 指標 ──
    ax_kd.plot(dates, plot_df['K'], color='#fdcb6e', lw=1.4, label='K')
    ax_kd.plot(dates, plot_df['D'], color='#e17055', lw=1.4, label='D')
    ax_kd.axhline(80, color='#ef5350', lw=0.8, ls='--', alpha=0.7)
    ax_kd.axhline(20, color='#26a69a', lw=0.8, ls='--', alpha=0.7)
    ax_kd.set_ylim(0, 100)
    ax_kd.set_ylabel('KD', fontsize=9)
    ax_kd.legend(loc='upper left', fontsize=8)
    ax_kd.grid(True)
 
    # X 軸格式
    ax_kd.xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.setp(ax_price.get_xticklabels(), visible=False)
    plt.setp(ax_vol.get_xticklabels(),   visible=False)
    plt.setp(ax_rsi.get_xticklabels(),   visible=False)
    plt.setp(ax_macd.get_xticklabels(),  visible=False)
    plt.xticks(rotation=30)
 
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()
 
# ═══════════════════════════════════════════════════════════
# 🏆 多股排名彙總
# ═══════════════════════════════════════════════════════════
 
def print_ranking(results_summary: list):
    results_summary.sort(key=lambda x: x[1], reverse=True)
    print("\n" + "═" * 60)
    print("  🏆 最終推薦排名（依評分由高到低）")
    print("═" * 60)
    medals = ['🥇', '🥈', '🥉'] + ['  '] * 20
    for i, (stock, score, verdict, name) in enumerate(results_summary):
        print(f"  {medals[i]}  {name:<20} ({stock:<12}) {score:+3d}分  {verdict}")
    print("═" * 60)
 
# ═══════════════════════════════════════════════════════════
# 📊 類股大盤 K 線比較圖
# ═══════════════════════════════════════════════════════════

def plot_sector_overview(stocks_data: list):
    """
    類股大盤綜覽圖（整潔版）
    stocks_data: list of (stock_code, df, info, result)

    版面：
      Row 0        : 標準化報酬率走勢（滿寬）
      Row 1..rows_k: 各股 K 線格（每列最多 3 欄）
      Row -1       : 評分橫條排名（滿寬）
    """
    n = len(stocks_data)
    if n == 0:
        return

    # ── 顏色池 ──
    PALETTE = [
        '#00d4ff', '#ffd700', '#ff6b6b', '#a29bfe',
        '#55efc4', '#fd79a8', '#fdcb6e', '#e17055',
        '#74b9ff', '#00cec9', '#fab1a0', '#6c5ce7',
    ]

    tail_n = 90          # 顯示最近 90 天
    cols   = min(n, 3)
    rows_k = (n + cols - 1) // cols

    # 排名列高度隨股票數動態調整（每支 0.6 英吋，至少 1.8）
    rank_h_ratio = max(1.8, n * 0.6)
    height_ratios = [3.0] + [2.8] * rows_k + [rank_h_ratio]
    total_rows    = 1 + rows_k + 1

    fig_w = max(cols * 6.5, 13)
    fig_h = sum(height_ratios) * 1.35
    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor('#0f0f1a')

    gs = gridspec.GridSpec(
        total_rows, cols,
        figure=fig,
        height_ratios=height_ratios,
        hspace=0.55, wspace=0.32,
        left=0.18, right=0.97, top=0.95, bottom=0.04
    )

    # ══════════════════════════════════════════
    # (A) 標準化報酬率走勢（滿寬）
    # ══════════════════════════════════════════
    ax_norm = fig.add_subplot(gs[0, :])
    ax_norm.set_facecolor('#1a1a2e')
    ax_norm.set_title('類股標準化報酬率走勢對比  ( 首日 = 100 )',
                       fontsize=12, fontweight='bold', color='#eeeeff', pad=10)

    for idx, (code, df, info, result) in enumerate(stocks_data):
        sub        = df.tail(tail_n).copy()
        normalized = (sub['Close'] / sub['Close'].iloc[0]) * 100
        color      = PALETTE[idx % len(PALETTE)]
        score_str  = f"{result['score']:+d}分"
        # 圖例只用股票代碼 + 分數，避免長名稱換行
        label = f"{code}  {score_str}"
        ax_norm.plot(sub.index, normalized, color=color, lw=2.0, label=label)
        # 右端數值標記
        ax_norm.annotate(
            f" {normalized.iloc[-1]:.1f}",
            xy=(sub.index[-1], normalized.iloc[-1]),
            fontsize=8.5, color=color, va='center',
        )

    ax_norm.axhline(100, color='#636e72', lw=0.9, ls='--', alpha=0.6, label='基準線 100')
    ax_norm.set_ylabel('報酬率指數', fontsize=10)
    ax_norm.legend(
        loc='upper left', fontsize=9, framealpha=0.65,
        ncol=min(n + 1, 6),          # 全放同一行（加上基準線）
        handlelength=1.5, columnspacing=1.2
    )
    ax_norm.grid(True, alpha=0.4)
    ax_norm.xaxis.set_major_locator(plt.MaxNLocator(8))
    plt.setp(ax_norm.get_xticklabels(), rotation=15, fontsize=8)

    # ══════════════════════════════════════════
    # (B) 各股 K 線子圖
    # ══════════════════════════════════════════
    for idx, (code, df, info, result) in enumerate(stocks_data):
        row_k = idx // cols
        col_k = idx % cols
        ax = fig.add_subplot(gs[1 + row_k, col_k])
        ax.set_facecolor('#1a1a2e')

        sub   = df.tail(tail_n).copy()
        dates = sub.index
        color = PALETTE[idx % len(PALETTE)]
        price = sub['Close'].iloc[-1]
        cur   = info.get('currency', '')

        # 蠟燭 K 線
        for date, row in sub.iterrows():
            o, h, l, c = row['Open'], row['High'], row['Low'], row['Close']
            bc = COLORS['volume_up'] if c >= o else COLORS['volume_dn']
            ax.plot([date, date], [l, h], color=bc, lw=0.7, zorder=2)
            rh = abs(c - o) or (h - l) * 0.01
            ax.bar(date, rh, bottom=min(o, c), color=bc, width=0.6, zorder=3, alpha=0.9)

        # MA 線
        ax.plot(dates, sub['MA5'],  color=COLORS['ma5'],  lw=1.0, label='MA5')
        ax.plot(dates, sub['MA20'], color=COLORS['ma20'], lw=1.0, label='MA20')
        if not sub['MA60'].isna().all():
            ax.plot(dates, sub['MA60'], color=COLORS['ma60'], lw=1.0, label='MA60')

        # 布林通道（極淡背景）
        ax.fill_between(dates, sub['BB_Upper'], sub['BB_Lower'],
                        alpha=0.04, color='#aaaaaa')
        ax.plot(dates, sub['BB_Upper'], color='#555577', lw=0.6, ls='--')
        ax.plot(dates, sub['BB_Lower'], color='#555577', lw=0.6, ls='--')

        # 最新價橫線
        ax.axhline(price, color=color, lw=0.7, ls=':', alpha=0.8)

        # 子圖標題：兩行 → 只用股票代碼避免過長
        verdict = result['verdict']
        ax.set_title(
            f"{code}   最新 {price:.1f} {cur}   {result['score']:+d}分  {verdict}",
            fontsize=8.5, color=color, pad=5
        )
        ax.legend(loc='upper left', fontsize=7, framealpha=0.5, ncol=3,
                  handlelength=1.2, columnspacing=0.8)
        ax.grid(True, alpha=0.35)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        plt.setp(ax.get_xticklabels(), rotation=15, fontsize=7)

    # 空格隱藏
    for empty in range(n, rows_k * cols):
        fig.add_subplot(gs[1 + empty // cols, empty % cols]).set_visible(False)

    # ══════════════════════════════════════════
    # (C) 評分橫條排名（滿寬）
    # ══════════════════════════════════════════
    ax_rank = fig.add_subplot(gs[-1, :])
    ax_rank.set_facecolor('#1a1a2e')

    sorted_data = sorted(stocks_data, key=lambda x: x[3]['score'], reverse=True)
    # Y 軸標籤只用 "代碼  公司簡稱"（最多 10 字截斷）
    def short_name(info, code):
        raw = info.get('name', code)
        return raw[:14] + '…' if len(raw) > 14 else raw

    labels = [f"{c}  {short_name(inf, c)}" for c, _, inf, _ in sorted_data]
    scores = [r['score'] for _, _, _, r in sorted_data]
    colors_bar = [
        '#00ff88' if s >= 6 else
        '#26a69a' if s >= 3 else
        '#f39c12' if s >= 0 else
        '#ef5350' if s >= -3 else '#ff0055'
        for s in scores
    ]

    bars = ax_rank.barh(labels, scores, color=colors_bar, height=0.55, zorder=3)
    for bar, score in zip(bars, scores):
        offset = 0.15 if score >= 0 else -0.15
        ha     = 'left' if score >= 0 else 'right'
        ax_rank.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            f'{score:+d}', va='center', ha=ha, fontsize=9.5, color='#eeeeff'
        )

    ax_rank.axvline(0, color='#636e72', lw=1.2)
    ax_rank.set_title('類股評分排名', fontsize=11, fontweight='bold',
                       color='#eeeeff', pad=8)
    ax_rank.set_xlabel('評分', fontsize=9)
    ax_rank.grid(True, axis='x', alpha=0.35, zorder=0)
    # 左邊留足空間給 Y 軸標籤
    ax_rank.tick_params(axis='y', labelsize=9)

    plt.show()


# ═══════════════════════════════════════════════════════════
# 🚀 主程式
# ═══════════════════════════════════════════════════════════
 
def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         🔍 專業股票分析系統 v2.0                         ║")
    print("║         Powered by Yahoo Finance                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  📌 輸入提示：")
    print("     台股：2330.TW , 2454.TW , 0050.TW")
    print("     美股：AAPL , NVDA , TSLA , MSFT")
    print("     港股：9988.HK , 0700.HK")
    print()
 
    user_input = input("  請輸入股票代碼（逗號分隔，例如 2330.TW,AAPL）：\n  > ").strip()
 
    if not user_input:
        print("  ⚠️  未輸入任何代碼，結束程式")
        return
 
    stocks = [s.strip().upper() for s in user_input.split(",") if s.strip()]
    results_summary = []
    stocks_data = []   # 用於類股大盤圖

    for stock in stocks:
        print(f"\n  🔄 正在分析 {stock}...")
        df, info = fetch_stock_data(stock, period="6mo")

        if df is None:
            continue

        result = analyze_stock(df, info)
        print_report(stock, df, info, result)
        plot_dashboard(stock, df, info, result)

        results_summary.append((
            stock,
            result['score'],
            result['verdict'],
            info.get('name', stock)
        ))
        stocks_data.append((stock, df, info, result))

    if len(results_summary) > 1:
        print_ranking(results_summary)

    # ── 類股大盤綜覽圖（多股才顯示）──
    if len(stocks_data) > 1:
        print("\n  📊 正在繪製類股大盤綜覽圖...")
        plot_sector_overview(stocks_data)

    print("\n  ⚠️  免責聲明：本分析僅供參考，不構成任何投資建議。投資有風險，請自行評估。")
 
 
if __name__ == "__main__":
    main()
