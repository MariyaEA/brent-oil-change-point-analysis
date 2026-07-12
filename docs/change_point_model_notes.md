# Change Point Model Understanding

A change point is a time index where the data-generating process changes. In the Brent oil context, the change may appear in the mean price, average return, volatility, trend, or several properties together.

## Initial Bayesian switch model

For a single mean shift, the model can be written as:

- `tau ~ DiscreteUniform(0, T - 1)`
- `mu_before ~ Normal(m, s)`
- `mu_after ~ Normal(m, s)`
- `sigma ~ HalfNormal(s_sigma)`
- `mu_t = mu_before` when `t < tau`, otherwise `mu_after`
- `y_t ~ Normal(mu_t, sigma)`

In PyMC, `pm.math.switch` selects the appropriate parameter on each side of `tau`. MCMC sampling produces a posterior distribution rather than one fixed answer.

## Expected outputs

- A posterior distribution for the change index and corresponding calendar date.
- Credible intervals showing uncertainty around the change date.
- Posterior estimates for before/after mean or volatility parameters.
- A distribution for the size and direction of the shift, including the probability that the after-period parameter is larger than the before-period parameter.
- Convergence diagnostics such as R-hat, effective sample size, and trace plots.

## Modeling implications from EDA

The interim EDA finds strong evidence that raw prices are non-stationary while log returns are stationary. It also shows volatility clustering, particularly during 2020. Therefore, the final analysis should not rely on a single constant-variance Normal model without sensitivity checks. A practical sequence is:

1. Fit a simple price-level mean-shift model as the required baseline.
2. Fit a return mean/volatility change model.
3. Compare robustness across selected market windows and alternative likelihoods.
4. Consider multiple change points if the posterior is broad or multimodal.

## Inherent limitations

A change point model detects structural breaks; it does not identify their cause. Event matching is a second, interpretive step that should be supported by external evidence and, where possible, explanatory variables or a causal research design.
