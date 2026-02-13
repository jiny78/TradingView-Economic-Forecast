# TradingView-Economic-Forecast

TradingView API를 활용한 경제 예측 프로그램

## 기능

- **실시간 기술적 분석** - TradingView의 오실레이터, 이동평균, 요약 신호 분석
- **경제 예측** - RSI, MACD, 스토캐스틱, ADX, CCI, 볼린저밴드 등 복합 지표 기반 방향 예측
- **웹 대시보드** - TradingView 차트 위젯, 경제 캘린더, 시장 개요 통합
- **CLI 모드** - 터미널에서 빠른 분석 및 예측 실행

## 지원 자산

| 카테고리 | 종목 |
|---------|------|
| 주요 지수 | S&P 500, Dow Jones, NASDAQ, KOSPI, KOSDAQ, Nikkei 225, Hang Seng |
| 외환 | EUR/USD, USD/JPY, USD/KRW, GBP/USD |
| 암호화폐 | Bitcoin, Ethereum |
| 원자재 | Gold, Silver, WTI Crude Oil |

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 웹 대시보드

```bash
python main.py
```

브라우저에서 `http://localhost:5000` 접속

### CLI 모드

```bash
# 전체 시장 분석
python main.py --cli

# 특정 종목 분석
python main.py --cli -s SPX
python main.py --cli -s BTCUSD

# 카테고리별 분석
python main.py --cli -c indices
python main.py --cli -c forex

# 시간대 변경
python main.py --cli -s SPX -i 1h
```

## 프로젝트 구조

```
├── main.py                    # 메인 엔트리포인트
├── requirements.txt           # Python 의존성
├── src/
│   ├── config.py              # 설정 관리
│   ├── data/
│   │   └── collector.py       # TradingView 데이터 수집
│   ├── analysis/
│   │   └── technical.py       # 기술적 분석
│   ├── forecast/
│   │   └── predictor.py       # 예측 엔진
│   └── web/
│       ├── app.py             # Flask 웹 애플리케이션
│       ├── templates/
│       │   └── index.html     # 대시보드 HTML
│       └── static/
│           ├── css/style.css  # 스타일시트
│           └── js/app.js      # 프론트엔드 JavaScript
└── .env.example               # 환경변수 예시
```

## 환경 변수

`.env.example`을 `.env`로 복사하여 설정:

```
FORECAST_DAYS=30
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

## 면책 조항

이 프로그램은 정보 제공 목적으로만 사용되며, 투자 조언이 아닙니다. 실제 투자 결정에 이 프로그램의 결과를 단독으로 사용하지 마십시오.
