# Git and GitHub Workflow for Final Submission

The final repository should show incremental work through task branches and pull requests. Do not upload the complete ZIP to `main` in one commit.

## Branch sequence

1. `main` — protected submission branch.
2. `task-1-foundation-eda` — workflow, event data, assumptions, EDA, and diagnostics.
3. `task-2-bayesian-change-point` — PyMC model, MCMC diagnostics, posterior figures, interpretation, and tests.
4. `task-3-dashboard` — Flask API, React dashboard, filters, screenshots, and API tests.
5. `final-documentation` — final README, report, and final consistency checks.

Each task branch should be merged into `main` through a pull request after tests pass.

## Suggested Task 2 commits

```text
feat: add reusable Bayesian change point model
feat: run PyMC sampling and save posterior artifacts
notebook: add executed Task 2 Bayesian analysis
viz: add posterior and convergence figures
test: add change point utility tests
docs: interpret detected shift and event association
```

## Suggested Task 3 commits

```text
feat: add Flask analysis API endpoints
feat: add responsive React dashboard shell
feat: add price chart event overlays and filters
feat: add model insight and event exploration components
test: add Flask endpoint tests
docs: add dashboard setup guide and screenshots
```

## Pull request checks

Before merging each branch:

```bash
pytest -q
cd dashboard/frontend
npm ci
npm run build
```

Confirm that GitHub Actions passes, review the changed files, then merge the pull request into `main`.
