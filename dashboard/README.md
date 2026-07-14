# Interactive Brent Oil Dashboard

The dashboard converts the Task 1 and Task 2 outputs into an interface for Birhan Energies' stakeholders. The Flask API serves historical prices, event data, event-window summaries, and Bayesian model results. The React frontend provides filters, event highlighting, change-point markers, model diagnostics, and responsive layouts.

![Desktop dashboard](../reports/dashboard/dashboard_desktop.png)

## Architecture

```text
React + Vite + Recharts
          │
          │ HTTP/JSON
          ▼
Flask API + CORS
          │
          ├── BrentOilPrices.csv
          ├── oil_market_events.csv
          ├── event_window_summary.csv
          └── change_point_results.json
```

## 1. Start the Flask backend

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python dashboard/backend/app.py
```

The API runs at `http://localhost:5000`.

### Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Service health check |
| `GET /api/prices` | Historical price data with date and frequency filters |
| `GET /api/events` | Researched events with date/category filters |
| `GET /api/change-points` | Bayesian posterior change-point result |
| `GET /api/event-correlations` | Descriptive event-window movements |
| `GET /api/summary` | Headline dataset and model indicators |

Example:

```bash
curl "http://localhost:5000/api/prices?start_date=2013-01-01&end_date=2016-12-31&frequency=weekly"
```

## 2. Start the React frontend

Open a second terminal:

```bash
cd dashboard/frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

## Production build

```bash
cd dashboard/frontend
npm ci
npm run build
npm run preview
```

## Dashboard interactions

- Select start and end dates.
- Change chart resolution between daily, weekly, and monthly.
- Filter researched events by category.
- Select an event to highlight its date on the price chart.
- Compare the Bayesian change point with the nearest event.
- Review descriptive five-observation event-window movements.

## Error handling

The API validates malformed dates, reversed date ranges, unsupported frequencies, missing files, and invalid source data. The frontend applies request timeouts and presents an actionable message when the API is unavailable.

## Interpretation guardrail

The event-window table and date overlays show temporal associations. They do not establish that an event caused a price movement.
