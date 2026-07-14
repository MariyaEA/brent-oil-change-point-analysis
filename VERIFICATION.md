# Verification Record

The final snapshot was validated before packaging.

- Python tests: **14 passed**
- React production build: **successful**
- Task 1 notebook: executed and saved with outputs
- Task 2 PyMC notebook: executed and saved with outputs
- MCMC chains: 4
- Maximum R-hat: 1.0017
- Minimum bulk ESS: 2,891
- Dashboard screenshots: desktop and mobile included
- Flask endpoints tested: health, prices, validation error, and change-point result

Re-run validation with:

```bash
pytest -q
cd dashboard/frontend
npm ci
npm run build
```
