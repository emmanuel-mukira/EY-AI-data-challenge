---
trigger: always_on
---
# EY AI Data Challenge — AI Model Safeguards & Rules

## Project Context

- **Competition:** EY AI Data Challenge
- **Goal:** Predict 3 water quality targets (ALKALINITY, SALINITY, PHOSPHORUS) using XGBoost on Snowflake
- **Data:** ~9,300 rows of satellite, weather, and water quality measurements
- **Target Metric:** R² ≥ 0.45
- **Infrastructure:** Snowflake (RAW / STAGING / ANALYTICS schemas), local Python environment

---

## HARD RULES — All AI Models Must Follow These

### 1. No Data Leakage — EVER

- **NEVER** use future data to predict past values. If a feature uses data from time `t+1` to predict time `t`, reject it immediately.
- **NEVER** include the target variable (ALKALINITY, SALINITY, PHOSPHORUS) or any derivative of it as a feature.
- **NEVER** use k-fold cross-validation on this time-series data. Only time-based splits are allowed.
- When creating lagged features (e.g., Rain_t-7), verify the lag direction is correct: the feature value must come from **before** the prediction date, never after.
- When joining tables, always verify the join does not leak future information. **Review every join that involves a date/time column line by line.**

### 2. Snowflake Credit Protection

- Default warehouse size: `X-Small`. Do not suggest scaling up unless explicitly asked.
- **NEVER** write queries that do full table scans on large tables without WHERE clauses.
- Expensive computations (distance to coast, elevation lookups) must be computed **once** and stored, never recomputed per batch or per model run.
- Always include `LIMIT` clauses during development/debugging queries.
- Prefer Snowpark push-down computation over pulling data to local Python.

### 3. Code Generation Rules

- **All generated code must be immediately runnable.** No placeholder functions, no `TODO` stubs in critical paths.
- Always include required imports at the top of the file.
- Every feature engineering function must have a **plain-English comment** explaining what the feature captures and why it matters for water quality prediction.
- When generating XGBoost code, always include `early_stopping_rounds` — never let trees grow unbounded.
- When generating SQL, always use explicit column names — no `SELECT *` in production queries.

### 4. Validation & Submission Integrity

- The validation split must be the **last 20% of the timeline**, not random.
- Never report a metric from training data as if it were a validation metric.
- When printing R² scores, always label which split (train/validation/test) the score comes from.
- Before any submission file is generated, verify: correct number of rows, correct column names, no NaN values in predictions.

### 5. Feature Engineering Guardrails

- **Lat/Lon cannot be used as raw features.** They must be transformed into meaningful signals (distance to coast, elevation, watershed ID, etc.).
- NDWI and NDVI formulas are fixed. Do not invent custom band ratios without explicit user approval.
  - `NDWI = (Green - NIR) / (Green + NIR)`
  - `NDVI = (NIR - Red) / (NIR + Red)`
- Seasonal encoding must use cyclical (sin/cos) transforms, not raw day-of-year integers.
- All features must be explainable in one sentence. If you can't explain it, don't create it.

### 6. Model Architecture Rules

- This is a **3-model problem**: one XGBoost model per target variable (Alkalinity, Salinity, Phosphorus).
- Do not combine targets into a single multi-output model.
- Each model may have different features and different hyperparameters — they are independent.
- Default hyperparameter safe zone:

```python
params = {
    'n_estimators': 500,
    'learning_rate': 0.03,
    'max_depth': 5,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'early_stopping_rounds': 50
}
```

- Do NOT grid-search unless explicitly asked. Feature signal matters more than tuning.

### 7. AI-Assisted Code Review Protocol

- **If it touches time or joins → the user reviews line by line.** Always flag these sections clearly.
- When generating Snowpark transformations, annotate which operations are pushed down to Snowflake vs executed locally.
- Never silently change the validation strategy, feature set, or model architecture. Always explain and get confirmation.
- When suggesting new features, state:
  1. What the feature captures
  2. Which target(s) it likely helps
  3. Whether it risks leakage
  4. Estimated compute cost (low/medium/high)

### 8. File & Schema Discipline

- Raw data goes in `RAW` schema only
- Transformed/engineered features go in `STAGING`
- Final model-ready tables go in `ANALYTICS`
- Local files follow this structure:
  - `data/` — raw CSV files (gitignored)
  - `notebooks/` — Jupyter notebooks
  - `src/` — Python modules
  - `models/` — saved model artifacts (gitignored)
  - `submissions/` — output CSV files for submission

### 9. Error Handling & Debugging

- When a model underperforms, diagnose with residual plots BEFORE adding complexity.
- If R² drops between submissions, revert to the last known good configuration before investigating.
- Always log: feature count, row count, train/val split sizes, and R² per target after each training run.

### 10. What NOT To Do

- ❌ Do not suggest neural networks, deep learning, or transformers for this problem
- ❌ Do not suggest ensembling multiple model types (stick to XGBoost)
- ❌ Do not add features that can't be explained in plain English
- ❌ Do not optimize for leaderboard position at the expense of reproducibility
- ❌ Do not delete or weaken validation logic to improve apparent scores
- ❌ Do not use random seeds inconsistently — always set `random_state=42`
