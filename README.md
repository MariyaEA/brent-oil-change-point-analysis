# Brent Oil Change Point Analysis

A time-series project for identifying structural breaks in Brent crude oil prices and examining how those breaks align with major geopolitical, OPEC/OPEC+, sanctions, supply, and economic events.

The work is framed for **Birhan Energies**, an energy-sector consultancy supporting investors, policymakers, and energy companies. The repository currently contains the complete Week 10 interim foundation: analysis workflow, event data, exploratory analysis, time-series diagnostics, change point model explanation, reproducible outputs, and tests.

## Interim scope

- Validates and cleans the daily Brent price dataset.
- Documents a complete workflow from loading to stakeholder insight.
- Provides a sourced event catalogue with 19 major events.
- Visualizes raw prices, daily log returns, rolling volatility, and event context.
- Tests stationarity using ADF and KPSS.
- Explains Bayesian change point outputs and limitations.
- Separates reusable code, scripts, notebooks, tests, reports, and documentation.

## Repository structure

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/task.md
│   └── workflows/unittests.yml
├── .vscode/settings.json
├── data/
│   ├── events/oil_market_events.csv
│   ├── raw/BrentOilPrices.csv
│   └── README.md
├── docs/
│   ├── analysis_workflow.md
│   ├── assumptions_and_limitations.md
│   └── change_point_model_notes.md
├── notebooks/
│   ├── 01_task1_eda.ipynb
│   └── README.md
├── reports/
│   ├── figures/
│   ├── eda_summary.json
│   ├── event_window_summary.csv
│   ├── interim_report.md
│   └── stationarity_results.csv
├── scripts/
│   └── run_eda.py
├── src/
│   ├── data_loader.py
│   ├── diagnostics.py
│   ├── features.py
│   └── plotting.py
├── tests/
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows, activate the environment with:

```bash
.venv\Scripts\activate
```

## Run the analysis

Open the executed notebook:

```bash
jupyter lab notebooks/01_task1_eda.ipynb
```

Reproduce all interim figures and tables from the command line:

```bash
python scripts/run_eda.py
```

Run the tests:

```bash
pytest
```

## Data

The challenge-provided Brent CSV contains **9,011 observations from 20 May 1987 to 14 November 2022**. Prices are recorded in U.S. dollars per barrel. The source file uses two date formats, and the loader parses both explicitly.

The researched event file includes its source name and URL in every row. It spans geopolitical conflicts, financial crises, sanctions, natural disasters, OPEC/OPEC+ policy decisions, and the COVID-19 demand shock.

## Initial findings

- Raw Brent prices show persistent shifts in level and are not stationary under the combined ADF/KPSS evidence.
- Daily log returns are stationary and are therefore more suitable for short-run return modeling.
- Volatility clusters strongly rather than remaining constant; the most extreme rolling volatility occurs during the 2020 oil-market disruption.
- The full 1987-2022 period contains several regimes, so a one-change-point model should be treated as a baseline and tested for robustness.

Detailed results are in the [executed EDA notebook](notebooks/01_task1_eda.ipynb) and [interim report](reports/interim_report.md).

## Interpretation guardrail

Change point detection identifies a structural shift in the time series. Matching that date to a researched event creates a plausible hypothesis, not proof of causal impact. The analysis reports temporal alignment, parameter uncertainty, competing explanations, and model limitations.

## Next phase

The next branch will implement Bayesian change point estimation in PyMC, assess convergence, quantify before/after parameter changes, and connect posterior change dates to the event catalogue. The final branch will expose results through a Flask API and an interactive React dashboard.

## Author

**Mariamawit Ewnetu Alemu**  
10 Academy — Artificial Intelligence Mastery
