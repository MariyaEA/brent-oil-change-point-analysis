# Assumptions and Limitations

## Assumptions

- The `Price` field represents a consistent daily Brent crude oil price in U.S. dollars per barrel.
- Observations are ordered trading-day records; weekends and market holidays are not treated as missing daily observations.
- All prices are positive, which allows log-return calculation.
- The dates in the event catalogue are reasonable reference dates for when information became public. Some conflicts and economic shocks developed over weeks or months, so a single date is an analytical simplification.
- A short event window can reveal temporal alignment, but the appropriate response window may differ by event type.
- The initial Bayesian model will assume a structural change that can be summarized through before/after parameters. This is intentionally simple and will be checked against richer alternatives.

## Limitations

- **Correlation in time is not causation.** A detected change point near an event does not establish that the event caused the price shift. Oil prices also react to inventories, exchange rates, interest rates, demand forecasts, speculation, weather, and other concurrent information.
- **Event dates may overlap.** Several events can occur in the same period, making attribution difficult without a causal design and additional covariates.
- **The raw price series is non-stationary.** A change in long-run price levels can dominate a single-switch model. Log returns are more suitable for short-run stationarity but answer a different question.
- **Volatility is time-varying.** Constant-variance Normal likelihoods can understate heavy tails and volatility clustering. Student-t errors, regime-switching variance, or GARCH-style extensions may be more appropriate.
- **One change point is restrictive.** The 1987-2022 period includes several market regimes. A single `tau` may identify only the strongest break and miss other important shifts.
- **Daily data do not capture intraday reactions.** Prices may react before an official announcement when information is anticipated or leaked.
- **Dataset coverage differs from the challenge description.** The provided CSV contains observations through 14 November 2022, while the challenge document describes coverage through 30 September 2022. The repository analyzes the file as received and records the observed date range explicitly.
- **No inflation adjustment is applied in the interim EDA.** Long-run nominal price comparisons therefore mix market movements with changes in the purchasing power of the U.S. dollar.

## Interpretation rule

The final report will use wording such as “the model identifies a structural shift near this event” or “the dates are consistent with a possible association.” It will not state that the model proves causal impact.
