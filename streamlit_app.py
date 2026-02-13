"""EconoVision - Streamlit 기반 경제 예측 대시보드

Streamlit Cloud 배포용 엔트리포인트.
실행: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd

from src.config import SYMBOLS, INTERVALS, DEFAULT_INTERVAL
from src.data.collector import fetch_analysis, fetch_multiple
from src.analysis.technical import analyze, analyze_multiple
from src.forecast.predictor import predict, predict_multiple

# ─── 페이지 설정 ───
st.set_page_config(
    page_title="EconoVision - Economic Forecast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 커스텀 CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* 전체 테마 */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* 메트릭 카드 */
div[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    backdrop-filter: blur(20px);
}

div[data-testid="stMetric"] label {
    font-size: 0.8rem !important;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95);
    border-right: 1px solid rgba(148, 163, 184, 0.1);
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.5rem;
}

/* 데이터프레임 */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.08);
}

/* 탭 */
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}

/* 커스텀 카드 */
.eco-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.08);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    backdrop-filter: blur(20px);
}

.eco-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.eco-card-name {
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9;
}

.eco-card-symbol {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.eco-card-price {
    font-size: 1.4rem;
    font-weight: 800;
    color: #f1f5f9;
    margin: 0.5rem 0;
    font-variant-numeric: tabular-nums;
}

.eco-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
}

.badge-up {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.badge-down {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.badge-neutral {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
}

.badge-buy {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.badge-sell {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.text-green { color: #10b981; }
.text-red { color: #ef4444; }
.text-amber { color: #f59e0b; }
.text-muted { color: #64748b; }

/* 프로그레스 바 */
.progress-bar {
    width: 100%;
    height: 6px;
    background: rgba(148, 163, 184, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin: 0.3rem 0;
}

.progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

/* 구분선 */
.eco-divider {
    border: none;
    border-top: 1px solid rgba(148, 163, 184, 0.1);
    margin: 1rem 0;
}

/* 게이지 */
.gauge-container {
    text-align: center;
    padding: 1rem 0;
}

/* 헤더 */
.eco-header {
    text-align: center;
    padding: 1rem 0 2rem;
}

.eco-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}

.eco-subtitle {
    color: #64748b;
    font-size: 0.9rem;
}

/* 면책조항 */
.disclaimer {
    text-align: center;
    color: #475569;
    font-size: 0.75rem;
    padding: 1.5rem 0;
    border-top: 1px solid rgba(148, 163, 184, 0.1);
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ─── 헬퍼 함수 ───

CATEGORY_LABELS = {
    "all": "전체",
    "indices": "주요 지수",
    "forex": "외환",
    "crypto": "암호화폐",
    "commodities": "원자재",
}

INTERVAL_LABELS = {
    "1m": "1분", "5m": "5분", "15m": "15분",
    "1h": "1시간", "4h": "4시간", "1d": "일간",
    "1W": "주간", "1M": "월간",
}

TREND_KR = {
    "STRONG_UPTREND": "강한 상승",
    "UPTREND": "상승",
    "SIDEWAYS": "횡보",
    "DOWNTREND": "하락",
    "STRONG_DOWNTREND": "강한 하락",
    "UNKNOWN": "-",
}

RECOMMENDATION_KR = {
    "STRONG_BUY": "강력 매수",
    "BUY": "매수",
    "NEUTRAL": "중립",
    "SELL": "매도",
    "STRONG_SELL": "강력 매도",
}


def fmt_number(num):
    if num is None:
        return "-"
    if abs(num) >= 1:
        return f"{num:,.2f}"
    return f"{num:.6f}"


def direction_badge(direction, direction_kr, emoji):
    cls = "badge-up" if direction == "UP" else "badge-down" if direction == "DOWN" else "badge-neutral"
    return f'<span class="eco-badge {cls}">{emoji} {direction_kr}</span>'


def summary_badge(rec):
    label = RECOMMENDATION_KR.get(rec, rec)
    if rec in ("STRONG_BUY", "BUY"):
        cls = "badge-buy"
    elif rec in ("STRONG_SELL", "SELL"):
        cls = "badge-sell"
    else:
        cls = "badge-neutral"
    return f'<span class="eco-badge {cls}">{label}</span>'


def confidence_bar(confidence):
    pct = confidence * 100
    if confidence >= 0.6:
        color = "#10b981"
    elif confidence >= 0.3:
        color = "#f59e0b"
    else:
        color = "#ef4444"
    return f'''
    <div class="progress-bar">
        <div class="progress-fill" style="width:{pct:.0f}%;background:{color}"></div>
    </div>
    <span style="font-size:0.8rem;color:#94a3b8;font-weight:600">{pct:.0f}%</span>
    '''


def get_symbols_for_category(category):
    if category == "all":
        all_syms = {}
        for cat_syms in SYMBOLS.values():
            all_syms.update(cat_syms)
        return all_syms
    return SYMBOLS.get(category, {})


# ─── 사이드바 ───

with st.sidebar:
    st.markdown("# 📈 EconoVision")
    st.markdown('<p style="color:#64748b;font-size:0.85rem;margin-top:-0.5rem">경제 예측 대시보드</p>', unsafe_allow_html=True)

    st.markdown("---")

    category = st.selectbox(
        "카테고리",
        options=list(CATEGORY_LABELS.keys()),
        format_func=lambda x: CATEGORY_LABELS[x],
        index=0,
    )

    interval = st.selectbox(
        "시간대",
        options=INTERVALS,
        format_func=lambda x: INTERVAL_LABELS.get(x, x),
        index=INTERVALS.index(DEFAULT_INTERVAL),
    )

    st.markdown("---")

    analyze_btn = st.button("🔍 분석 시작", use_container_width=True, type="primary")

    st.markdown("---")

    # 개별 종목 분석
    st.markdown("#### 개별 종목 분석")
    all_symbols_flat = {}
    for cat_syms in SYMBOLS.values():
        all_symbols_flat.update(cat_syms)

    symbol_options = {f"{name} ({key})": key for key, (_, name) in all_symbols_flat.items()}
    selected_label = st.selectbox("종목 선택", options=list(symbol_options.keys()))
    selected_key = symbol_options[selected_label] if selected_label else None

    detail_btn = st.button("📊 상세 분석", use_container_width=True)

    st.markdown("---")
    st.markdown(
        '<p style="color:#475569;font-size:0.7rem;text-align:center">'
        '본 서비스는 정보 제공 목적이며<br>투자 결정의 근거로 사용 불가</p>',
        unsafe_allow_html=True,
    )


# ─── 메인 헤더 ───

st.markdown("""
<div class="eco-header">
    <div class="eco-title">EconoVision</div>
    <div class="eco-subtitle">TradingView API 기반 실시간 경제 예측 대시보드</div>
</div>
""", unsafe_allow_html=True)


# ─── 시장 개요 분석 ───

if analyze_btn:
    symbols = get_symbols_for_category(category)

    if not symbols:
        st.warning("해당 카테고리에 종목이 없습니다.")
    else:
        progress_bar = st.progress(0, text="시장 데이터를 수집하고 있습니다...")

        try:
            # 데이터 수집
            market_data = fetch_multiple(symbols, interval)
            progress_bar.progress(40, text="기술적 분석 중...")

            if not market_data:
                progress_bar.empty()
                st.error("데이터를 가져올 수 없습니다. 네트워크 연결을 확인하세요.")
            else:
                # 실패한 종목 알림
                failed = set(symbols.keys()) - set(market_data.keys())
                if failed:
                    st.warning(f"일부 종목 데이터 수집 실패: {', '.join(failed)}")

                # 분석
                analyses = analyze_multiple(market_data)
                progress_bar.progress(70, text="예측 생성 중...")

                # 예측
                forecasts = predict_multiple(market_data)
                progress_bar.progress(100, text="완료!")
                progress_bar.empty()

                # 결과를 세션에 저장
                st.session_state["results"] = {
                    "analyses": analyses,
                    "forecasts": forecasts,
                    "category": category,
                    "interval": interval,
                }
        except Exception as e:
            progress_bar.empty()
            st.error(f"분석 중 오류가 발생했습니다: {e}")

if "results" in st.session_state:
    res = st.session_state["results"]
    analyses = res["analyses"]
    forecasts = res["forecasts"]

    # ── 요약 카드 ──
    bullish = sum(1 for f in forecasts.values() if f.direction == "UP")
    bearish = sum(1 for f in forecasts.values() if f.direction == "DOWN")
    neutral = sum(1 for f in forecasts.values() if f.direction == "NEUTRAL")
    total = len(forecasts)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("상승 예측", f"{bullish}개", delta=f"{bullish/total*100:.0f}%" if total else "0%")
    col2.metric("보합 예측", f"{neutral}개")
    col3.metric("하락 예측", f"{bearish}개", delta=f"-{bearish/total*100:.0f}%" if total else "0%")
    col4.metric("분석 종목", f"{total}개")

    st.markdown("")

    # ── 탭: 카드뷰 / 테이블뷰 ──
    tab_cards, tab_table = st.tabs(["📊 카드 뷰", "📋 테이블 뷰"])

    with tab_cards:
        cols = st.columns(3)
        for i, key in enumerate(analyses):
            a = analyses[key]
            f = forecasts[key]
            change_cls = "text-green" if a.change_pct >= 0 else "text-red"
            change_prefix = "+" if a.change_pct >= 0 else ""
            dir_badge = direction_badge(f.direction, f.direction_kr, f.direction_emoji)
            sum_badge = summary_badge(a.summary_recommendation)
            conf_bar = confidence_bar(f.confidence)
            trend_text = TREND_KR.get(a.trend, a.trend)

            card_html = f'''
            <div class="eco-card">
                <div class="eco-card-header">
                    <div>
                        <div class="eco-card-symbol">{key}</div>
                        <div class="eco-card-name">{a.name}</div>
                    </div>
                    {dir_badge}
                </div>
                <div class="eco-card-price">{fmt_number(a.price)}</div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
                    <span class="{change_cls}" style="font-weight:600">{change_prefix}{a.change_pct:.2f}%</span>
                    {sum_badge}
                </div>
                <hr class="eco-divider">
                <div style="display:flex;gap:1rem">
                    <div style="flex:1">
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">신뢰도</div>
                        {conf_bar}
                    </div>
                    <div style="flex:1">
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">추세</div>
                        <div style="font-size:0.85rem;font-weight:600;margin-top:0.3rem">{trend_text}</div>
                    </div>
                    <div style="flex:1">
                        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em">시그널</div>
                        <div style="font-size:0.85rem;font-weight:600;margin-top:0.3rem">{f.signal_strength}</div>
                    </div>
                </div>
            </div>
            '''
            cols[i % 3].markdown(card_html, unsafe_allow_html=True)

    with tab_table:
        table_data = []
        for key in analyses:
            a = analyses[key]
            f = forecasts[key]
            table_data.append({
                "종목": key,
                "이름": a.name,
                "가격": fmt_number(a.price),
                "변동률": f"{a.change_pct:+.2f}%",
                "분석": RECOMMENDATION_KR.get(a.summary_recommendation, a.summary_recommendation),
                "추세": TREND_KR.get(a.trend, a.trend),
                "예측": f"{f.direction_emoji} {f.direction_kr}",
                "신뢰도": f"{f.confidence*100:.0f}%",
                "시그널": f.signal_strength,
            })
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ─── 개별 종목 상세 분석 ───

if detail_btn and selected_key:
    tv_symbol, display_name = all_symbols_flat[selected_key]

    try:
        with st.spinner(f"{display_name} 분석 중..."):
            data = fetch_analysis(tv_symbol, interval, display_name)
    except Exception as e:
        st.error(f"{display_name} 데이터 수집 실패: {e}")
        data = None

    if data is None:
        st.error(f"{display_name} 데이터를 가져올 수 없습니다. 종목/시간대를 변경해 보세요.")
    else:
        a = analyze(data)
        f = predict(data)

        st.markdown("---")
        st.markdown(f"## 📊 {a.name} ({a.symbol}) 상세 분석")

        # 가격 & 예측 요약
        col_price, col_forecast, col_tech = st.columns(3)

        with col_price:
            change_color = "green" if a.change_pct >= 0 else "red"
            st.metric("현재가", fmt_number(a.price), delta=f"{a.change_pct:+.2f}%")
            st.markdown(f"**추세:** {TREND_KR.get(a.trend, a.trend)}")

        with col_forecast:
            dir_color = "🟢" if f.direction == "UP" else "🔴" if f.direction == "DOWN" else "🟡"
            st.metric("예측 방향", f"{f.direction_emoji} {f.direction_kr}")
            st.metric("신뢰도", f"{f.confidence*100:.1f}%")

        with col_tech:
            st.metric("시그널 강도", f"{f.signal_strength}")
            st.markdown(f"**종합:** {RECOMMENDATION_KR.get(a.summary_recommendation, a.summary_recommendation)}")

        # 기술적 분석 상세
        st.markdown("### 기술적 분석")
        col_osc, col_ma = st.columns(2)

        with col_osc:
            st.markdown(f"""
            <div class="eco-card">
                <div class="eco-card-name" style="margin-bottom:0.8rem">오실레이터</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
                    <span>{summary_badge(a.oscillator_recommendation)}</span>
                    <span style="color:#94a3b8;font-size:0.85rem">{RECOMMENDATION_KR.get(a.oscillator_recommendation, a.oscillator_recommendation)}</span>
                </div>
                <div style="display:flex;gap:1rem;margin-top:0.5rem">
                    <span class="text-green" style="font-weight:600">매수 {a.oscillator_buy}</span>
                    <span class="text-muted" style="font-weight:600">중립 {a.oscillator_neutral}</span>
                    <span class="text-red" style="font-weight:600">매도 {a.oscillator_sell}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_ma:
            st.markdown(f"""
            <div class="eco-card">
                <div class="eco-card-name" style="margin-bottom:0.8rem">이동평균</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
                    <span>{summary_badge(a.ma_recommendation)}</span>
                    <span style="color:#94a3b8;font-size:0.85rem">{RECOMMENDATION_KR.get(a.ma_recommendation, a.ma_recommendation)}</span>
                </div>
                <div style="display:flex;gap:1rem;margin-top:0.5rem">
                    <span class="text-green" style="font-weight:600">매수 {a.ma_buy}</span>
                    <span class="text-muted" style="font-weight:600">중립 {a.ma_neutral}</span>
                    <span class="text-red" style="font-weight:600">매도 {a.ma_sell}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 주요 가격대
        if a.key_levels:
            st.markdown("### 주요 가격대")
            level_cols = st.columns(len(a.key_levels))
            for i, (lk, lv) in enumerate(a.key_levels.items()):
                level_cols[i % len(level_cols)].metric(lk, fmt_number(lv))

        # 분석 팩터
        if f.factors:
            st.markdown("### 분석 팩터")
            factor_data = [{"지표": k, "분석": v} for k, v in f.factors.items()]
            st.dataframe(pd.DataFrame(factor_data), use_container_width=True, hide_index=True)


# ─── TradingView 위젯 ───

st.markdown("---")

tv_tab1, tv_tab2, tv_tab3 = st.tabs(["📈 실시간 차트", "🌍 글로벌 시장", "📅 경제 캘린더"])

with tv_tab1:
    # 차트 종목 선택
    chart_options = {}
    for cat_syms in SYMBOLS.values():
        for key, (tv_sym, name) in cat_syms.items():
            chart_options[f"{name} ({key})"] = tv_sym

    chart_label = st.selectbox("차트 종목", list(chart_options.keys()), key="chart_select")
    chart_symbol = chart_options[chart_label]

    st.components.v1.html(f"""
    <div id="tv-chart" style="height:500px"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
        container_id: "tv-chart",
        autosize: true,
        symbol: "{chart_symbol}",
        interval: "D",
        timezone: "Asia/Seoul",
        theme: "dark",
        style: "1",
        locale: "kr",
        toolbar_bg: "#0a0e1a",
        enable_publishing: false,
        allow_symbol_change: true,
        studies: ["MASimple@tv-basicstudies","RSI@tv-basicstudies","MACD@tv-basicstudies"],
        hide_side_toolbar: false,
        withdateranges: true,
    }});
    </script>
    """, height=520)

with tv_tab2:
    st.components.v1.html("""
    <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <script type="text/javascript"
            src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
        {
            "colorTheme": "dark",
            "dateRange": "1D",
            "showChart": true,
            "locale": "kr",
            "width": "100%",
            "height": 500,
            "isTransparent": true,
            "showSymbolLogo": true,
            "showFloatingTooltip": true,
            "tabs": [
                {"title":"지수","symbols":[{"s":"SP:SPX","d":"S&P 500"},{"s":"DJ:DJI","d":"Dow Jones"},{"s":"NASDAQ:IXIC","d":"NASDAQ"},{"s":"KRX:KOSPI","d":"KOSPI"},{"s":"TVC:NI225","d":"Nikkei 225"}]},
                {"title":"외환","symbols":[{"s":"FX_IDC:EURUSD","d":"EUR/USD"},{"s":"FX_IDC:USDJPY","d":"USD/JPY"},{"s":"FX_IDC:USDKRW","d":"USD/KRW"},{"s":"FX_IDC:GBPUSD","d":"GBP/USD"}]},
                {"title":"암호화폐","symbols":[{"s":"BITSTAMP:BTCUSD","d":"Bitcoin"},{"s":"BITSTAMP:ETHUSD","d":"Ethereum"}]},
                {"title":"원자재","symbols":[{"s":"TVC:GOLD","d":"Gold"},{"s":"TVC:SILVER","d":"Silver"},{"s":"TVC:USOIL","d":"WTI Oil"}]}
            ]
        }
        </script>
    </div>
    """, height=520)

with tv_tab3:
    st.components.v1.html("""
    <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <script type="text/javascript"
            src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
        {
            "colorTheme": "dark",
            "isTransparent": true,
            "width": "100%",
            "height": 450,
            "locale": "kr",
            "importanceFilter": "-1,0,1",
            "currencyFilter": "USD,EUR,JPY,KRW,GBP,CNY"
        }
        </script>
    </div>
    """, height=470)


# ─── 면책조항 ───

st.markdown("""
<div class="disclaimer">
    EconoVision | TradingView API 기반 경제 예측 대시보드<br>
    본 서비스는 정보 제공 목적이며, 투자 결정의 근거로 사용해서는 안 됩니다.
</div>
""", unsafe_allow_html=True)
