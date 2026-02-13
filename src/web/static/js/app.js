// TradingView Economic Forecast - Frontend Application

document.addEventListener("DOMContentLoaded", () => {
  initTradingViewChart();
  initTechnicalWidget();
  initMarketOverviewWidget();
  initEconomicCalendarWidget();
});

// ── TradingView Chart Widget ──

let tvWidget = null;

function initTradingViewChart() {
  const symbolSelect = document.getElementById("chart-symbol-select");
  const symbol = symbolSelect ? symbolSelect.value : "SP:SPX";

  if (typeof TradingView === "undefined") {
    console.warn("TradingView library not loaded");
    return;
  }

  tvWidget = new TradingView.widget({
    container_id: "tv-chart-widget",
    autosize: true,
    symbol: symbol,
    interval: "D",
    timezone: "Asia/Seoul",
    theme: "dark",
    style: "1",
    locale: "kr",
    toolbar_bg: "#1e222d",
    enable_publishing: false,
    allow_symbol_change: true,
    studies: ["MASimple@tv-basicstudies", "RSI@tv-basicstudies", "MACD@tv-basicstudies"],
    hide_side_toolbar: false,
    withdateranges: true,
    save_image: true,
  });

  if (symbolSelect) {
    symbolSelect.addEventListener("change", () => {
      const newSymbol = symbolSelect.value;
      if (tvWidget && tvWidget.iframe) {
        tvWidget.iframe.contentWindow.postMessage(
          { name: "set-symbol", data: { symbol: newSymbol } },
          "*"
        );
      }
      // Re-init chart with new symbol
      document.getElementById("tv-chart-widget").innerHTML = "";
      tvWidget = new TradingView.widget({
        container_id: "tv-chart-widget",
        autosize: true,
        symbol: newSymbol,
        interval: "D",
        timezone: "Asia/Seoul",
        theme: "dark",
        style: "1",
        locale: "kr",
        toolbar_bg: "#1e222d",
        enable_publishing: false,
        allow_symbol_change: true,
        studies: ["MASimple@tv-basicstudies", "RSI@tv-basicstudies", "MACD@tv-basicstudies"],
        hide_side_toolbar: false,
        withdateranges: true,
        save_image: true,
      });
    });
  }
}

// ── TradingView Technical Analysis Widget ──

function initTechnicalWidget() {
  const container = document.getElementById("tv-technical-widget");
  if (!container) return;

  container.innerHTML = `
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
    </div>`;

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js";
  script.async = true;
  script.textContent = JSON.stringify({
    interval: "1D",
    width: "100%",
    isTransparent: true,
    height: 400,
    symbol: "SP:SPX",
    showIntervalTabs: true,
    locale: "kr",
    colorTheme: "dark",
  });
  container.querySelector(".tradingview-widget-container").appendChild(script);
}

// ── TradingView Market Overview Widget ──

function initMarketOverviewWidget() {
  const container = document.getElementById("tv-market-widget");
  if (!container) return;

  container.innerHTML = `
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
    </div>`;

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js";
  script.async = true;
  script.textContent = JSON.stringify({
    colorTheme: "dark",
    dateRange: "1D",
    showChart: true,
    locale: "kr",
    width: "100%",
    height: 500,
    largeChartUrl: "",
    isTransparent: true,
    showSymbolLogo: true,
    showFloatingTooltip: true,
    tabs: [
      {
        title: "지수",
        symbols: [
          { s: "SP:SPX", d: "S&P 500" },
          { s: "DJ:DJI", d: "Dow Jones" },
          { s: "NASDAQ:IXIC", d: "NASDAQ" },
          { s: "KRX:KOSPI", d: "KOSPI" },
          { s: "TVC:NI225", d: "Nikkei 225" },
        ],
      },
      {
        title: "외환",
        symbols: [
          { s: "FX_IDC:EURUSD", d: "EUR/USD" },
          { s: "FX_IDC:USDJPY", d: "USD/JPY" },
          { s: "FX_IDC:USDKRW", d: "USD/KRW" },
          { s: "FX_IDC:GBPUSD", d: "GBP/USD" },
        ],
      },
      {
        title: "암호화폐",
        symbols: [
          { s: "BITSTAMP:BTCUSD", d: "Bitcoin" },
          { s: "BITSTAMP:ETHUSD", d: "Ethereum" },
        ],
      },
      {
        title: "원자재",
        symbols: [
          { s: "TVC:GOLD", d: "Gold" },
          { s: "TVC:SILVER", d: "Silver" },
          { s: "TVC:USOIL", d: "WTI Oil" },
        ],
      },
    ],
  });
  container.querySelector(".tradingview-widget-container").appendChild(script);
}

// ── TradingView Economic Calendar Widget ──

function initEconomicCalendarWidget() {
  const container = document.getElementById("tv-calendar-widget");
  if (!container) return;

  container.innerHTML = `
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
    </div>`;

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "https://s3.tradingview.com/external-embedding/embed-widget-events.js";
  script.async = true;
  script.textContent = JSON.stringify({
    colorTheme: "dark",
    isTransparent: true,
    width: "100%",
    height: 400,
    locale: "kr",
    importanceFilter: "-1,0,1",
    currencyFilter: "USD,EUR,JPY,KRW,GBP,CNY",
  });
  container.querySelector(".tradingview-widget-container").appendChild(script);
}

// ── API Calls ──

async function loadOverview() {
  const category = document.getElementById("category-select").value;
  const interval = document.getElementById("interval-select").value;
  const loading = document.getElementById("loading");
  const tbody = document.getElementById("overview-body");

  loading.style.display = "block";
  tbody.innerHTML = "";

  try {
    const resp = await fetch(
      `/api/overview?category=${encodeURIComponent(category)}&interval=${encodeURIComponent(interval)}`
    );
    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.error || "Failed to load data");
    }

    if (data.results.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" class="empty-msg">데이터가 없습니다.</td></tr>`;
      return;
    }

    data.results.forEach((item) => {
      const row = document.createElement("tr");
      const changeCls = item.change_pct >= 0 ? "text-green" : "text-red";
      const summaryBadge = getSummaryBadge(item.summary);
      const dirBadge = getDirectionBadge(item.direction, item.direction_kr, item.direction_emoji);
      const confBar = getConfidenceBar(item.confidence);
      const signalBar = getSignalBar(item.signal_strength);

      row.innerHTML = `
        <td><strong>${item.symbol}</strong></td>
        <td>${item.name}</td>
        <td>${formatNumber(item.price)}</td>
        <td class="${changeCls}">${item.change_pct >= 0 ? "+" : ""}${item.change_pct.toFixed(2)}%</td>
        <td>${summaryBadge}</td>
        <td>${formatTrend(item.trend)}</td>
        <td>${dirBadge}</td>
        <td>${confBar}</td>
        <td>${signalBar}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-msg text-red">오류: ${err.message}</td></tr>`;
  } finally {
    loading.style.display = "none";
  }
}

async function analyzeSymbol() {
  const select = document.getElementById("chart-symbol-select");
  const tvSymbol = select.value;
  const name = select.options[select.selectedIndex].dataset.name || "";
  const interval = document.getElementById("interval-select").value;
  const section = document.getElementById("analysis-detail");

  try {
    const resp = await fetch(
      `/api/analyze?symbol=${encodeURIComponent(tvSymbol)}&interval=${encodeURIComponent(interval)}&name=${encodeURIComponent(name)}`
    );
    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.error || "Analysis failed");
    }

    renderAnalysisDetail(data);
    section.style.display = "block";
    section.scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    alert("분석 실패: " + err.message);
  }
}

// ── Render Functions ──

function renderAnalysisDetail(data) {
  const { analysis: a, forecast: f } = data;

  // Price info
  const changeCls = a.change_pct >= 0 ? "text-green" : "text-red";
  document.getElementById("price-info").innerHTML = `
    <div class="detail-item">
      <span class="detail-label">종목</span>
      <span class="detail-value">${a.name} (${a.symbol})</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">현재가</span>
      <span class="detail-value">${formatNumber(a.price)}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">변동률</span>
      <span class="detail-value ${changeCls}">${a.change_pct >= 0 ? "+" : ""}${a.change_pct.toFixed(2)}%</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">추세</span>
      <span class="detail-value">${formatTrend(a.trend)}</span>
    </div>
    ${renderKeyLevels(a.key_levels)}
  `;

  // Forecast info
  const dirCls = f.direction === "UP" ? "text-green" : f.direction === "DOWN" ? "text-red" : "text-yellow";
  document.getElementById("forecast-info").innerHTML = `
    <div class="detail-item">
      <span class="detail-label">예측 방향</span>
      <span class="detail-value ${dirCls}">${f.direction_emoji} ${f.direction_kr}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">신뢰도</span>
      <span class="detail-value">${(f.confidence * 100).toFixed(1)}%</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">시그널 강도</span>
      <span class="detail-value">${f.signal_strength}</span>
    </div>
    ${getSignalBar(f.signal_strength)}
  `;

  // Technical info
  document.getElementById("technical-info").innerHTML = `
    <div class="detail-item">
      <span class="detail-label">종합</span>
      <span class="detail-value">${getSummaryBadge(a.summary)} ${a.summary_kr}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">오실레이터</span>
      <span class="detail-value">${getSummaryBadge(a.oscillator)} ${a.oscillator_kr}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">이동평균</span>
      <span class="detail-value">${getSummaryBadge(a.ma)} ${a.ma_kr}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">오실레이터</span>
      <span class="detail-value text-green">매수 ${a.oscillator_counts.buy}</span>
      <span class="detail-value text-neutral">중립 ${a.oscillator_counts.neutral}</span>
      <span class="detail-value text-red">매도 ${a.oscillator_counts.sell}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">이동평균</span>
      <span class="detail-value text-green">매수 ${a.ma_counts.buy}</span>
      <span class="detail-value text-neutral">중립 ${a.ma_counts.neutral}</span>
      <span class="detail-value text-red">매도 ${a.ma_counts.sell}</span>
    </div>
  `;

  // Factors
  const factorsHtml = Object.entries(f.factors)
    .map(
      ([key, val]) => `
      <div class="detail-item">
        <span class="detail-label">${key}</span>
        <span class="detail-value">${val}</span>
      </div>`
    )
    .join("");
  document.getElementById("factors-info").innerHTML = factorsHtml || '<p class="text-neutral">팩터 데이터 없음</p>';
}

function renderKeyLevels(levels) {
  if (!levels || Object.keys(levels).length === 0) return "";
  return Object.entries(levels)
    .map(
      ([key, val]) => `
      <div class="detail-item">
        <span class="detail-label">${key}</span>
        <span class="detail-value">${formatNumber(val)}</span>
      </div>`
    )
    .join("");
}

// ── Helper Functions ──

function formatNumber(num) {
  if (num === null || num === undefined) return "-";
  if (Math.abs(num) >= 1) {
    return num.toLocaleString("ko-KR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  return num.toFixed(6);
}

function getSummaryBadge(rec) {
  const map = {
    STRONG_BUY: '<span class="badge badge-buy">강력매수</span>',
    BUY: '<span class="badge badge-buy">매수</span>',
    NEUTRAL: '<span class="badge badge-neutral">중립</span>',
    SELL: '<span class="badge badge-sell">매도</span>',
    STRONG_SELL: '<span class="badge badge-sell">강력매도</span>',
  };
  return map[rec] || `<span class="badge badge-neutral">${rec}</span>`;
}

function getDirectionBadge(dir, kr, emoji) {
  const cls = dir === "UP" ? "badge-up" : dir === "DOWN" ? "badge-down" : "badge-neutral";
  return `<span class="badge ${cls}">${emoji} ${kr}</span>`;
}

function formatTrend(trend) {
  const map = {
    STRONG_UPTREND: '<span class="text-green">강한 상승</span>',
    UPTREND: '<span class="text-green">상승</span>',
    SIDEWAYS: '<span class="text-yellow">횡보</span>',
    DOWNTREND: '<span class="text-red">하락</span>',
    STRONG_DOWNTREND: '<span class="text-red">강한 하락</span>',
    UNKNOWN: '<span class="text-neutral">-</span>',
  };
  return map[trend] || `<span class="text-neutral">${trend}</span>`;
}

function getConfidenceBar(confidence) {
  const pct = (confidence * 100).toFixed(0);
  const color = confidence >= 0.6 ? "var(--accent-green)" : confidence >= 0.3 ? "var(--accent-yellow)" : "var(--accent-red)";
  return `
    <div class="signal-meter">
      <div class="signal-fill" style="width:${pct}%;background:${color}"></div>
    </div>
    <small>${pct}%</small>
  `;
}

function getSignalBar(strength) {
  // strength is -100 to 100, center at 50%
  const pct = ((strength + 100) / 2).toFixed(0);
  const color = strength > 20 ? "var(--accent-green)" : strength < -20 ? "var(--accent-red)" : "var(--accent-yellow)";
  return `
    <div class="signal-meter">
      <div class="signal-fill" style="width:${pct}%;background:${color}"></div>
    </div>
    <small>${strength}</small>
  `;
}
