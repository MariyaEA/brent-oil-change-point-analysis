# B9W10 Interim Report: Brent Oil Change Point Analysis

**Author:** Mariamawit Ewnetu Alemu  
**Program:** 10 Academy — Artificial Intelligence Mastery  
**Challenge:** Week 10, Change Point Analysis and Statistical Modeling of Time Series Data

## 1. Purpose and workflow

Birhan Energies needs to understand when Brent oil prices moved into new statistical regimes and whether those shifts occurred near major geopolitical, OPEC, sanctions, or economic events. My workflow starts with strict data validation, then moves through exploratory analysis, stationarity and volatility diagnostics, Bayesian change point modeling, event comparison, and stakeholder interpretation. The final step will communicate not only the estimated change date and parameter shift, but also posterior uncertainty and the limitations of event attribution.

The repository separates reusable code from analysis. `src/data_loader.py` validates the two date formats found in the CSV, checks schema and prices, and sorts observations. `src/features.py` calculates log returns and rolling volatility. `src/diagnostics.py` applies ADF and KPSS tests, while `scripts/run_eda.py` reproduces the notebook outputs from the command line. The event catalogue contains 19 researched events with source links and an explicitly labeled hypothesized direction.

## 2. Initial EDA findings

The provided dataset contains **9,011 daily observations from 20 May 1987 to 14 November 2022**. The average nominal price is approximately **$48.42 per barrel**, while the median is **$38.57**. The highest observed price is **$143.95 on 3 July 2008**, and the lowest is **$9.10 on 10 December 1998**.

The raw series shows long price cycles, large shocks, and persistent changes in level. Statistical testing supports this visual pattern. The Augmented Dickey-Fuller test on price fails to reject a unit root at the 5% level, while KPSS rejects level stationarity. In contrast, daily log returns strongly reject the ADF unit-root null, and KPSS does not reject stationarity. This means the raw price level is useful for describing economically meaningful regime shifts, but log returns are more appropriate for short-run stationary modeling.

Volatility is not constant. Large returns occur in clusters, and the 30-observation rolling annualized volatility reaches its highest level in early May 2020. The largest one-day log-return movements also concentrate around the COVID-19 demand collapse and the extreme April 2020 oil-market dislocation. A constant-variance Normal model is therefore a transparent baseline, not a complete description of the process.

## 3. Change point model understanding

The required Bayesian switch model treats the change index, `tau`, as unknown. A discrete uniform prior allows the change to occur at any candidate observation. Before and after `tau`, the likelihood uses different parameters such as `mu_before` and `mu_after`; `pm.math.switch` selects the relevant parameter for each observation. MCMC then estimates posterior distributions for the change date and the before/after values.

Expected outputs include a posterior distribution for `tau`, its corresponding calendar-date interval, posterior distributions for the parameters on both sides, and a quantified shift such as the percentage difference in average price. R-hat values close to 1, adequate effective sample sizes, and well-mixed trace plots will be required before interpretation. A sharp posterior for `tau` indicates stronger date certainty, while a broad or multimodal posterior may indicate multiple plausible breaks or an overly simple model.

The EDA suggests that the final work should include the required price-level model and at least one sensitivity analysis using log returns or changing volatility. Since the full period contains many regimes, a single change point may identify only the most dominant break. Multiple-change-point or regime-switching extensions will be considered if the baseline posterior is not stable.

## 4. Events, assumptions, and limitations

The event CSV includes conflicts, sanctions, natural disasters, financial shocks, and OPEC/OPEC+ decisions. Dates are used as comparison anchors, not verified treatment dates. The descriptive event-window table reports price movements around each date, but those values are not causal effects.

The central limitation is that temporal correlation does not prove causation. Oil prices may react to several events at once, anticipated information, inventories, exchange rates, interest rates, demand revisions, weather, and market positioning. Daily data also miss intraday reactions, and one official event date may simplify a longer process. For this reason, the final report will describe detected breaks as being **near**, **aligned with**, or **consistent with** researched events. It will not claim that a date match proves an event caused the shift.

## 5. Interim conclusion

The repository now provides a reproducible foundation for Bayesian change point analysis. The price series is non-stationary, log returns are stationary, and volatility changes materially through time. These findings directly affect model design: price levels support interpretable regime shifts, while returns and volatility diagnostics are needed to avoid overstating a simple mean-change model. The next task is to fit and diagnose the PyMC model, quantify posterior before/after differences, and compare high-probability change dates with the event catalogue.
