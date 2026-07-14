# Bayesian Change Point Interpretation

## Result

The targeted PyMC model covers 1 September 2014 through 31 March 2015. It estimates a posterior median change date of **1 December 2014**, with an approximate 94% posterior date interval from **28 November to 4 December 2014**.

The posterior mean price shifts from **$88.24 per barrel** before the change to **$56.18 per barrel** afterward. This is an estimated decline of **36.3%**, and the posterior probability that the after-period mean is lower than the before-period mean is effectively 1.00.

## Convergence

The maximum R-hat across `tau`, `mu_before`, `mu_after`, and `sigma` is **1.0017**. The minimum bulk effective sample size is above **2,800**. The trace plot shows overlapping, stable chains. These diagnostics support posterior interpretation for this model specification.

## Event association

The nearest researched event is OPEC's **27 November 2014** decision to maintain its 30 million barrels-per-day production ceiling. The posterior median is four calendar days after that event, and the posterior interval begins one day afterward.

This timing is consistent with a possible association between continued production, oversupply expectations, and the transition to a lower price regime. It does not prove that the OPEC decision alone caused the decline. Prices had already been falling, and other drivers included global demand expectations, U.S. shale output, inventories, exchange rates, and market anticipation.

## Scope

The result is a focused case study based on a single mean-shift model. It should not be interpreted as a complete model of every structural change in the 1987–2022 Brent series.
