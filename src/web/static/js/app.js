// ═══════════════════════════════════════════════════════════
// EconoVision - Frontend Application
// ═══════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  initClock();
  initCategoryTabs();
  initTradingViewChart();
  initTechnicalWidget();
  initMarketOverviewWidget();
  initEconomicCalendarWidget();
});

// ── State ──
let currentCategory = "all";
let autoRefreshInterval = null;
let tvWidget = null;

// ── Clock ──
function initClock() {
  const el = document.getElementById("current-time");
  if (!el) return;

  function update() {
    const now = new Date();
    el.textContent = now.toLocaleString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  }
  update();
  setInterval(update, 1000);
}

// ── Category Tabs ──
function initCategoryTabs() {
  const tabs = document.querySelectorAll("#category-tabs .tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      currentCategory = tab.dataset.category;
    });
  });
}

// ── Auto Refresh ──
function toggleAutoRefresh() {
  const btn = document.getElementById("auto-refresh-btn");
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
    btn.classList.remove("active");
  } else {
    loadOverview();
    autoRefreshInterval = setInterval(loadOverview, 60000);
    btn.classList.add("active");
  }
}

// ── TradingView Chart Widget ──
function initTradingViewChart() {
  const symbolSelect = document.getElementById("chart-symbol-select");
  const symbol = symbolSelect ? symbolSelect.value : "SP:SPX";

  if (typeof TradingView === "undefined") {
    console.warn("TradingView library not loaded");
    return;
  }

  createChart(symbol);

  if (symbolSelect) {
    symbolSelect.addEventListener("change", () => {
      const container = document.getElementById("tv-chart-widget");
      container.innerHTML = "";
      createChart(symbolSelect.value);
    });
  }
}

function createChart(symbol) {
  tvWidget = new TradingView.widget({
    container_id: "tv-chart-widget",
    autosize: true,
    symbol: symbol,
    interval: "D",
    timezone: "Asia/Seoul",
    theme: "dark",
    style: "1",
    locale: "kr",
    toolbar_bg: "#0a0e1a",
    enable_publishing: false,
    allow_symbol_change: true,
    studies: [
      "MASimple@tv-basicstudies",
      "RSI@tv-basicstudies",
      "MACD@tv-basicstudies",
    ],
    hide_side_toolbar: false,
    withdateranges: true,
    save_image: true,
  });
}

// ── TradingView Technical Analysis Widget ──
function initTechnicalWidget() {
  const container = document.getElementById("tv-technical-widget");
  if (!container) return;

  container.innerHTML = `<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div></div>`;

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src =
    "https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js";
  script.async = true;
  script.textContent = JSON.stringify({
    interval: "1D",
    width: "100%",
    isTransparent: true,
    height: 380,
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

  container.innerHTML = `<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div></div>`;

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src =
    "https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js";
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

  container.innerHTML = `<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div></div>`;

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src =
    "https://s3.tradingview.com/external-embedding/embed-widget-events.js";
  script.async = true;
  script.textContent = JSON.stringify({
    colorTheme: "dark",
    isTransparent: true,
    width: "100%",
    height: 380,
    locale: "kr",
    importanceFilter: "-1,0,1",
    currencyFilter: "USD,EUR,JPY,KRW,GBP,CNY",
  });
  container.querySelector(".tradingview-widget-container").appendChild(script);
}

// ═══════════════════════════════════════════════════════════
// API Calls
// ═══════════════════════════════════════════════════════════

async function loadOverview() {
  const interval = document.getElementById("interval-select").value;
  const loading = document.getElementById("loading");
  const grid = document.getElementById("market-grid");
  const cardsGrid = document.getElementById("cards-grid");
  const summaryCards = document.getElementById("summary-cards");

  loading.style.display = "flex";
  grid.style.display = "none";
  summaryCards.style.display = "none";

  try {
    const resp = await fetch(
      `/api/overview?category=${encodeURIComponent(currentCategory)}&interval=${encodeURIComponent(interval)}`
    );
    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.error || "Failed to load data");
    }

    if (data.results.length === 0) {
      cardsGrid.innerHTML = `<div class="loading-content"><p class="loading-text">데이터가 없습니다.</p></div>`;
      grid.style.display = "block";
      return;
    }

    // Update summary counts
    let bullish = 0,
      bearish = 0,
      neutral = 0;
    data.results.forEach((item) => {
      if (item.direction === "UP") bullish++;
      else if (item.direction === "DOWN") bearish++;
      else neutral++;
    });

    document.getElementById("bullish-count").textContent = bullish;
    document.getElementById("neutral-count").textContent = neutral;
    document.getElementById("bearish-count").textContent = bearish;
    document.getElementById("total-count").textContent = data.results.length;
    summaryCards.style.display = "grid";

    // Update last update time
    const now = new Date();
    document.getElementById("last-update").textContent =
      `마지막 업데이트: ${now.toLocaleTimeString("ko-KR")}`;

    // Render market cards
    cardsGrid.innerHTML = data.results.map((item) => renderMarketCard(item)).join("");

    grid.style.display = "block";

    // Add click handlers
    cardsGrid.querySelectorAll(".market-card").forEach((card) => {
      card.addEventListener("click", () => {
        const symbol = card.dataset.symbol;
        const name = card.dataset.name;
        openDetailModal(symbol, name, interval);
      });
    });
  } catch (err) {
    cardsGrid.innerHTML = `<div class="loading-content"><p class="loading-text text-red">오류: ${escapeHtml(err.message)}</p></div>`;
    grid.style.display = "block";
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

async function openDetailModal(tvSymbol, name, interval) {
  const modal = document.getElementById("detail-modal");
  const title = document.getElementById("modal-title");
  const body = document.getElementById("modal-body");

  title.textContent = name;
  body.innerHTML = `
    <div class="loading-content" style="padding:2rem">
      <div class="loading-spinner"><div class="spinner-ring"></div><div class="spinner-ring"></div><div class="spinner-ring"></div></div>
      <p class="loading-text">분석 중...</p>
    </div>`;
  modal.style.display = "flex";

  try {
    const resp = await fetch(
      `/api/analyze?symbol=${encodeURIComponent(tvSymbol)}&interval=${encodeURIComponent(interval)}&name=${encodeURIComponent(name)}`
    );
    const data = await resp.json();

    if (!resp.ok) throw new Error(data.error || "Analysis failed");

    title.textContent = `${data.analysis.name} (${data.analysis.symbol})`;
    body.innerHTML = renderModalContent(data);
  } catch (err) {
    body.innerHTML = `<p class="text-red" style="padding:2rem;text-align:center">분석 실패: ${escapeHtml(err.message)}</p>`;
  }
}

function closeModal() {
  document.getElementById("detail-modal").style.display = "none";
}

// Close modal on overlay click
document.addEventListener("click", (e) => {
  if (e.target.id === "detail-modal") closeModal();
});

// Close modal on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

// ═══════════════════════════════════════════════════════════
// Render Functions
// ═══════════════════════════════════════════════════════════

function renderMarketCard(item) {
  const changeCls = item.change_pct >= 0 ? "text-green" : "text-red";
  const changePrefix = item.change_pct >= 0 ? "+" : "";
  const dirCls =
    item.direction === "UP"
      ? "dir-up"
      : item.direction === "DOWN"
        ? "dir-down"
        : "dir-neutral";
  const cardCls =
    item.direction === "UP"
      ? "card-up"
      : item.direction === "DOWN"
        ? "card-down"
        : "card-flat";
  const confPct = (item.confidence * 100).toFixed(0);
  const confColor = getConfidenceColor(item.confidence);
  const signalPct = ((item.signal_strength + 100) / 2).toFixed(0);
  const signalColor = getSignalColor(item.signal_strength);
  const summaryBadge = getSummaryBadge(item.summary);
  const trendText = getTrendText(item.trend);

  return `
    <div class="market-card ${cardCls}" data-symbol="${escapeAttr(item.symbol)}" data-name="${escapeAttr(item.name)}">
      <div class="card-top-row">
        <div class="card-symbol-info">
          <span class="card-symbol">${escapeHtml(item.key)}</span>
          <span class="card-name">${escapeHtml(item.name)}</span>
        </div>
        <div class="card-direction ${dirCls}">
          ${item.direction_emoji} ${item.direction_kr}
        </div>
      </div>
      <div class="card-middle-row">
        <span class="card-price">${formatNumber(item.price)}</span>
        <span class="card-change ${changeCls}">${changePrefix}${item.change_pct.toFixed(2)}%</span>
      </div>
      <div class="card-bottom-row">
        <div class="card-metric">
          <span class="metric-label">분석 ${summaryBadge}</span>
        </div>
        <div class="card-metric">
          <span class="metric-label">신뢰도</span>
          <div class="metric-bar"><div class="metric-fill" style="width:${confPct}%;background:${confColor}"></div></div>
          <span class="metric-value">${confPct}%</span>
        </div>
        <div class="card-metric">
          <span class="metric-label">시그널</span>
          <div class="metric-bar"><div class="metric-fill" style="width:${signalPct}%;background:${signalColor}"></div></div>
          <span class="metric-value">${item.signal_strength}</span>
        </div>
      </div>
    </div>`;
}

function renderModalContent(data) {
  const { analysis: a, forecast: f } = data;
  const changeCls = a.change_pct >= 0 ? "text-green" : "text-red";
  const changePrefix = a.change_pct >= 0 ? "+" : "";
  const dirCls =
    f.direction === "UP"
      ? "text-green"
      : f.direction === "DOWN"
        ? "text-red"
        : "text-amber";
  const confPct = (f.confidence * 100).toFixed(1);
  const confColor = getConfidenceColor(f.confidence);

  // Gauge
  const circumference = 2 * Math.PI * 50;
  const dashOffset = circumference * (1 - f.confidence);

  let html = `
    <!-- Price Section -->
    <div class="modal-section">
      <div class="modal-section-title">가격 정보</div>
      <div class="modal-row">
        <span class="modal-label">현재가</span>
        <span class="modal-value">${formatNumber(a.price)}</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">변동률</span>
        <span class="modal-value ${changeCls}">${changePrefix}${a.change_pct.toFixed(2)}%</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">추세</span>
        <span class="modal-value">${getTrendText(a.trend)}</span>
      </div>
    </div>

    <!-- Forecast Gauge -->
    <div class="modal-section">
      <div class="modal-section-title">예측 결과</div>
      <div class="gauge-container">
        <div class="gauge-ring">
          <svg width="120" height="120" viewBox="0 0 120 120">
            <circle class="gauge-bg" cx="60" cy="60" r="50"/>
            <circle class="gauge-fill" cx="60" cy="60" r="50"
              stroke="${confColor}"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${dashOffset}"/>
          </svg>
          <div class="gauge-center">
            <div class="gauge-value ${dirCls}">${f.direction_emoji}</div>
            <div class="gauge-label">${f.direction_kr}</div>
          </div>
        </div>
      </div>
      <div class="modal-row">
        <span class="modal-label">신뢰도</span>
        <span class="modal-value" style="color:${confColor}">${confPct}%</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">시그널 강도</span>
        <span class="modal-value">${f.signal_strength}</span>
      </div>
    </div>

    <!-- Technical Analysis -->
    <div class="modal-section">
      <div class="modal-section-title">기술적 분석</div>
      <div class="modal-row">
        <span class="modal-label">종합</span>
        <span class="modal-value">${getSummaryBadge(a.summary)} ${a.summary_kr}</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">오실레이터</span>
        <span class="modal-value">${getSummaryBadge(a.oscillator)} ${a.oscillator_kr}</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">이동평균</span>
        <span class="modal-value">${getSummaryBadge(a.ma)} ${a.ma_kr}</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">오실레이터 시그널</span>
        <span class="modal-value">
          <span class="text-green">매수 ${a.oscillator_counts.buy}</span> /
          <span class="text-muted">중립 ${a.oscillator_counts.neutral}</span> /
          <span class="text-red">매도 ${a.oscillator_counts.sell}</span>
        </span>
      </div>
      <div class="modal-row">
        <span class="modal-label">이동평균 시그널</span>
        <span class="modal-value">
          <span class="text-green">매수 ${a.ma_counts.buy}</span> /
          <span class="text-muted">중립 ${a.ma_counts.neutral}</span> /
          <span class="text-red">매도 ${a.ma_counts.sell}</span>
        </span>
      </div>
    </div>`;

  // Key Levels
  if (a.key_levels && Object.keys(a.key_levels).length > 0) {
    html += `<div class="modal-section"><div class="modal-section-title">주요 가격대</div>`;
    for (const [key, val] of Object.entries(a.key_levels)) {
      html += `<div class="modal-row"><span class="modal-label">${escapeHtml(key)}</span><span class="modal-value">${formatNumber(val)}</span></div>`;
    }
    html += `</div>`;
  }

  // Factors
  if (f.factors && Object.keys(f.factors).length > 0) {
    html += `<div class="modal-section"><div class="modal-section-title">분석 팩터</div>`;
    for (const [key, val] of Object.entries(f.factors)) {
      html += `<div class="modal-row"><span class="modal-label">${escapeHtml(key)}</span><span class="modal-value">${escapeHtml(String(val))}</span></div>`;
    }
    html += `</div>`;
  }

  return html;
}

function renderAnalysisDetail(data) {
  const { analysis: a, forecast: f } = data;

  // Price info
  const changeCls = a.change_pct >= 0 ? "text-green" : "text-red";
  document.getElementById("price-info").innerHTML = `
    <div class="detail-item">
      <span class="detail-label">종목</span>
      <span class="detail-value">${escapeHtml(a.name)} (${escapeHtml(a.symbol)})</span>
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
      <span class="detail-value">${getTrendText(a.trend)}</span>
    </div>
    ${renderKeyLevels(a.key_levels)}
  `;

  // Forecast info
  const dirCls =
    f.direction === "UP"
      ? "text-green"
      : f.direction === "DOWN"
        ? "text-red"
        : "text-amber";
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
      <span class="detail-value">
        <span class="text-green">매수 ${a.oscillator_counts.buy}</span> /
        <span class="text-muted">중립 ${a.oscillator_counts.neutral}</span> /
        <span class="text-red">매도 ${a.oscillator_counts.sell}</span>
      </span>
    </div>
    <div class="detail-item">
      <span class="detail-label">이동평균</span>
      <span class="detail-value">
        <span class="text-green">매수 ${a.ma_counts.buy}</span> /
        <span class="text-muted">중립 ${a.ma_counts.neutral}</span> /
        <span class="text-red">매도 ${a.ma_counts.sell}</span>
      </span>
    </div>
  `;

  // Factors
  const factorsHtml = Object.entries(f.factors)
    .map(
      ([key, val]) => `
      <div class="detail-item">
        <span class="detail-label">${escapeHtml(key)}</span>
        <span class="detail-value">${escapeHtml(String(val))}</span>
      </div>`
    )
    .join("");
  document.getElementById("factors-info").innerHTML =
    factorsHtml || '<p class="text-muted" style="font-size:0.85rem">팩터 데이터 없음</p>';
}

function renderKeyLevels(levels) {
  if (!levels || Object.keys(levels).length === 0) return "";
  return Object.entries(levels)
    .map(
      ([key, val]) => `
      <div class="detail-item">
        <span class="detail-label">${escapeHtml(key)}</span>
        <span class="detail-value">${formatNumber(val)}</span>
      </div>`
    )
    .join("");
}

// ═══════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════

function formatNumber(num) {
  if (num === null || num === undefined) return "-";
  if (Math.abs(num) >= 1) {
    return num.toLocaleString("ko-KR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
  return num.toFixed(6);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function getSummaryBadge(rec) {
  const map = {
    STRONG_BUY: '<span class="badge badge-buy">강력매수</span>',
    BUY: '<span class="badge badge-buy">매수</span>',
    NEUTRAL: '<span class="badge badge-neutral">중립</span>',
    SELL: '<span class="badge badge-sell">매도</span>',
    STRONG_SELL: '<span class="badge badge-sell">강력매도</span>',
  };
  return map[rec] || `<span class="badge badge-neutral">${escapeHtml(rec || "-")}</span>`;
}

function getTrendText(trend) {
  const map = {
    STRONG_UPTREND: '<span class="text-green">강한 상승</span>',
    UPTREND: '<span class="text-green">상승</span>',
    SIDEWAYS: '<span class="text-amber">횡보</span>',
    DOWNTREND: '<span class="text-red">하락</span>',
    STRONG_DOWNTREND: '<span class="text-red">강한 하락</span>',
    UNKNOWN: '<span class="text-muted">-</span>',
  };
  return map[trend] || `<span class="text-muted">${escapeHtml(trend || "-")}</span>`;
}

function getConfidenceColor(confidence) {
  if (confidence >= 0.6) return "var(--accent-green)";
  if (confidence >= 0.3) return "var(--accent-amber)";
  return "var(--accent-red)";
}

function getSignalColor(strength) {
  if (strength > 20) return "var(--accent-green)";
  if (strength < -20) return "var(--accent-red)";
  return "var(--accent-amber)";
}

function getConfidenceBar(confidence) {
  const pct = (confidence * 100).toFixed(0);
  const color = getConfidenceColor(confidence);
  return `
    <div class="signal-meter">
      <div class="signal-fill" style="width:${pct}%;background:${color}"></div>
    </div>
    <small>${pct}%</small>
  `;
}

function getSignalBar(strength) {
  const pct = ((strength + 100) / 2).toFixed(0);
  const color = getSignalColor(strength);
  return `
    <div class="signal-meter">
      <div class="signal-fill" style="width:${pct}%;background:${color}"></div>
    </div>
    <small>${strength}</small>
  `;
}
