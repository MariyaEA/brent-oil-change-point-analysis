# Data

## `raw/BrentOilPrices.csv`

Daily Brent crude oil prices supplied with the 10 Academy Week 10 challenge. The file has two fields:

- `Date`: observation date in one of two formats (`20-May-87` or `Nov 14, 2022`)
- `Price`: U.S. dollars per barrel

The file committed here is small and required to reproduce the notebook. The `.gitignore` excludes other raw files by default so large datasets are not added accidentally.

The actual file contains 9,011 observations from 20 May 1987 through 14 November 2022. This end date is later than the date stated in the challenge brief, so the discrepancy is documented as a limitation.

## `events/oil_market_events.csv`

A researched catalogue of major geopolitical, OPEC/OPEC+, sanctions, supply-disruption, and macroeconomic events. The `hypothesized_short_term_pressure` field is a prior expectation for exploration, not a causal label or observed result. Source links are included in each row.
