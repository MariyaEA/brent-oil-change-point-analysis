# Brent Oil Change Point Analysis

A complete time-series analysis and decision-intelligence project for detecting structural breaks in Brent crude oil prices and examining how those breaks align with major geopolitical, OPEC/OPEC+, sanctions, supply, and economic events.

The project is framed for **Birhan Energies**, an energy-sector consultancy supporting investors, policymakers, analysts, and energy companies.

![Birhan Energies dashboard](reports/dashboard/dashboard_desktop.png)

## Project objectives

1. Identify key events and structural changes that affected Brent oil prices.
2. Quantify before/after price regimes using Bayesian statistical modeling.
3. Deliver clear, interactive insights for stakeholder decision-making.

The analysis treats event timing and detected structural breaks as **associations**. Temporal alignment does not by itself establish causal impact.

## Final result

The targeted PyMC model analyzes the 1 September 2014–31 March 2015 market window and identifies:

| Output | Estimate |
|---|---:|
| Posterior median change date | **1 December 2014** |
| Approximate 94% date interval | **28 Nov–4 Dec 2014** |
| Mean price before | **$88.24/bbl** |
| Mean price after | **$56.18/bbl** |
| Estimated level shift | **−36.3%** |
| Maximum R-hat | **1.0017** |
| Nearest researched event | **OPEC maintains 30 million b/d ceiling, 27 Nov 2014** |

The date alignment is consistent with continued oversupply expectations after the OPEC decision, but it is not proof that the decision alone caused the price decline.

## What is included

### Task 1 — Analysis foundation

- Reproducible workflow from loading to insight generation
- Structured catalogue of 19 geopolitical, OPEC/OPEC+, sanctions, supply, and economic events
- Explicit assumptions and correlation-versus-causation limitations
- Raw price and log-return visualizations
- Trend, ADF/KPSS stationarity, and volatility analysis
- Reusable loading, feature, diagnostic, and plotting modules

### Task 2 — Bayesian change point modeling

- PyMC switch-point model with `tau`, `mu_before`, `mu_after`, and `sigma`
- `pm.math.switch` likelihood construction
- Four-chain MCMC sampling with convergence diagnostics
- Trace, tau-posterior, parameter-posterior, and posterior-predictive plots
- Quantified before/after price shift
- Written event association with an interpretation guardrail

### Task 3 — Flask/React dashboard

- Flask endpoints for historical prices, change-point results, events, and event-window movements
- React + Vite + Recharts interface
- Date range, resolution, and event-category filtering
- Event overlays, change-point markers, and event highlighting
- Responsive desktop and mobile design
- API and frontend error handling
- Committed dashboard screenshots

## Repository structure

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/task.md
│   └── workflows/unittests.yml
├── dashboard/
│   ├── backend/
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── src/components/
│   │   ├── src/services/
│   │   ├── package.json
│   │   └── vite.config.js
│   └── README.md
├── data/
│   ├── events/oil_market_events.csv
│   └── raw/BrentOilPrices.csv
├── docs/
│   ├── analysis_workflow.md
│   ├── assumptions_and_limitations.md
│   ├── change_point_model_notes.md
│   └── git_workflow.md
├── notebooks/
│   ├── 01_task1_eda.ipynb
│   └── 02_task2_bayesian_change_point.ipynb
├── reports/
│   ├── dashboard/
│   ├── figures/
│   ├── model/
│   ├── final_report.md
│   └── interim_report.md
├── scripts/
│   ├── generate_dashboard_screenshots.py
│   ├── run_change_point.py
│   └── run_eda.py
├── src/
│   ├── change_point.py
│   ├── data_loader.py
│   ├── diagnostics.py
│   ├── features.py
│   └── plotting.py
├── tests/
├── requirements.txt
└── README.md
```

## Python setup

Python 3.11 is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
```

## Run Task 1 EDA

```bash
python scripts/run_eda.py
jupyter lab notebooks/01_task1_eda.ipynb
```

## Run Task 2 Bayesian model

The fully executed notebook is committed:

```bash
jupyter lab notebooks/02_task2_bayesian_change_point.ipynb
```

Reproduce the saved model artifacts and figures:

```bash
python scripts/run_change_point.py
```

The command saves:

- `reports/model/mcmc_summary.csv`
- `reports/model/posterior_samples.csv`
- `reports/model/change_point_results.json`
- model diagnostic and posterior figures in `reports/figures/`

## Run the dashboard

### Terminal 1 — Flask API

```bash
python dashboard/backend/app.py
```

### Terminal 2 — React frontend

```bash
cd dashboard/frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

Detailed instructions and API documentation are in [`dashboard/README.md`](dashboard/README.md).

## API endpoints

| Endpoint | Description |
|---|---|
| `/api/health` | Backend health |
| `/api/prices` | Filtered historical prices |
| `/api/events` | Filtered researched events |
| `/api/change-points` | Posterior change-point result |
| `/api/event-correlations` | Descriptive event-window movements |
| `/api/summary` | Headline indicators |

## Testing

```bash
pytest -q
```

The repository contains data-loader, feature-engineering, change-point helper, and Flask API tests.

Build the frontend:

```bash
cd dashboard/frontend
npm ci
npm run build
```

GitHub Actions runs both the Python tests and the React production build on pushes and pull requests.

## Git workflow

The intended branch strategy is:

- `task-1-foundation-eda`
- `task-2-bayesian-change-point`
- `task-3-dashboard`
- `final-documentation`
- `main`

Each task branch should be merged to `main` through a pull request after CI passes. A detailed commit and PR plan is available in [`docs/git_workflow.md`](docs/git_workflow.md).

## Key limitations

- A single switch point cannot represent every oil-market regime.
- The baseline Normal model simplifies heavy tails and volatility clustering.
- Results depend partly on the selected event window.
- Daily data do not represent intraday reactions or market anticipation.
- Descriptive event windows and date matches are not causal estimates.
- Nominal prices are not inflation-adjusted.

## Reports

- [Interim report](reports/interim_report.md)
- [Final analytical report](reports/final_report.md)
- [Bayesian result interpretation](reports/model/change_point_interpretation.md)

## Author

**Mariamawit Ewnetu Alemu**  
10 Academy — Artificial Intelligence Mastery
