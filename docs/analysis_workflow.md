# Analysis Workflow

## Business question

Birhan Energies needs a defensible way to identify major shifts in Brent crude oil prices and compare those shifts with geopolitical, OPEC, sanctions, and macroeconomic events. The analysis is intended to support risk discussions and strategic planning, not to prove that one event caused a price movement.

## Planned workflow

1. **Load and validate the data.** Read the daily Brent price file, parse both date formats explicitly, convert prices to numeric values, check missing values and duplicates, and sort chronologically.
2. **Build the event catalogue.** Maintain a structured CSV of researched oil-market events with dates, categories, short descriptions, hypothesized price pressure, and source links.
3. **Explore the raw series.** Plot daily prices, summarize the range and distribution, and inspect long-run trends, shocks, and recovery periods.
4. **Create modeling features.** Calculate log prices, daily log returns, a rolling price mean, and rolling annualized volatility. Raw prices are retained for level-shift interpretation, while log returns support stationarity and volatility analysis.
5. **Test time-series properties.** Use ADF and KPSS tests together. ADF tests for a unit root; KPSS tests level stationarity. Their combined evidence guides whether a model should target price levels, returns, or both.
6. **Define candidate change point models.** Begin with a Bayesian single-switch model in PyMC, where the unknown change index `tau` selects different before/after parameters. Extend to multiple change points or variance changes if diagnostics show that one break is too restrictive.
7. **Estimate and diagnose.** Run MCMC sampling, inspect trace plots, posterior distributions, effective sample sizes, and R-hat values. Posterior uncertainty around `tau`, means, and volatility parameters will be reported rather than reduced to one deterministic date.
8. **Connect statistical shifts to events.** Compare posterior change dates with the researched event catalogue using transparent time windows. A close date match will be framed as temporal alignment and a hypothesis for further investigation.
9. **Generate stakeholder insight.** Translate posterior estimates into before/after price or volatility changes, explain uncertainty, and state limitations. Results will later be exposed through a Flask API and React dashboard.

## Interim output

The interim repository provides the validated event dataset, a fully executed EDA notebook, modular data and feature code, reproducible figures, stationarity results, tests, and this workflow. Bayesian estimation and dashboard implementation are reserved for later task branches.
