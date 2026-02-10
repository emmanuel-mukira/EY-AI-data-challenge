# EY AI Data Challenge — 7-Day Execution Roadmap

**Goal:** Deploy 3 specialized XGBoost models leveraging Snowflake's compute to maximize environmental signal and minimize noise. Target: R² ≥ 0.45.

---

## Task Checklist

- [x] **Day 0** — Infrastructure & Environment Hardening
- [x] **Day 1** — Snowflake-First Baseline (in progress)
- [ ] **Day 2** — Advanced Feature Engineering
- [ ] **Day 3** — Model Architecture & Validation Strategy
- [ ] **Day 4** — Industrial Training & First Submission
- [ ] **Day 5** — Tuning & Feature Pruning
- [ ] **Day 6** — Sanity Check & Error Analysis
- [ ] **Day 7** — Final Polish & Phase 2 Prep

---

## DAY 0: Infrastructure & Environment Hardening

Before touching the data, ensure your "factory" is built.

- **Snowflake Environment:**
  - Initialize your 120-day trial
  - Create a specific `EY_CHALLENGE` database
  - Separate schemas: `RAW`, `STAGING`, `ANALYTICS` (keeps feature engineering organized)
- **Compute Setup:**
  - Warehouse set to `X-Small` (save credits), auto-resume ON
- **Local Dev Environment:**
  - Use `conda` or `venv` to isolate dependencies
  - Key packages: `snowflake-snowpark-python`, `xgboost`, `scikit-learn`, `matplotlib`, `seaborn`

---

## DAY 1: The "Snowflake-First" Baseline

Don't rush to Python. Let Snowflake handle the heavy lifting.

- **Data Ingestion:** Load provided `.csv` files into `RAW` tables
- **Snowpark Integration:** Connect local Jupyter notebook to Snowflake via `Session` object
- **The Baseline Run:**
  - Execute the EY-provided benchmark
  - **Target Metric:** Confirm you can reproduce R² ≈ 0.20 locally
  - **Data Audit:** Check for missing values in targets (`ALKALINITY`, `SALINITY`, `PHOSPHORUS`)

---

## DAY 2: Advanced Feature Engineering (The Winning Margin)

This is where the challenge is won. Translate raw satellite and weather data into "bio-chemical signals."

### Environmental Indices (Satellite Data)

- **NDWI (Normalized Difference Water Index):** Excellent for moisture and turbidity
  - `NDWI = (Green - NIR) / (Green + NIR)`
- **NDVI (Normalized Difference Vegetation Index):** Captures runoff from surrounding flora
  - `NDVI = (NIR - Red) / (NIR + Red)`

### Hydrological Context (Replacing Lat/Lon)

- **Distance to Coast:** Calculate distance from station to nearest coastline
  - Derive from **public coastline shapefiles**
  - Calculate **once**, store it — do NOT recompute per batch (wastes credits)
  - Helps **Salinity** strongly; may be neutral/noisy for **Phosphorus** — keep target-specific
- **Elevation (SRTM):** Use high-resolution DEMs for "flow-direction" potential

### Temporal Dynamics

- **Lagged Variables:** Create 7-day and 14-day lags for rainfall (Rain_t-7, Rain_t-14) — accounts for runoff travel time
- **Seasonal Encoding:** Cyclical encoding (Sine/Cosine) for Day of Year
  - Helps smooth residuals, not create signal
  - Use **after** rainfall lags are working (lower priority if short on time)

---

## DAY 3: Model Architecture & Validation Strategy

Stop treating this as one problem; it is three distinct chemical puzzles.

### The "Triple-Threat" Strategy

- **Model A (Alkalinity):** Focus on geological features and long-term weather trends
- **Model B (Salinity):** Focus on evaporation rates and distance to sea
- **Model C (Phosphorus):** Focus on agricultural runoff indices (NDVI) and recent heavy rainfall

### Validation Logic

- **Strict Time-Series Split:** Do NOT use k-fold cross-validation
- Use the last 20% of the timeline as your "Hold-out" set to simulate the real competition leaderboard

---

## DAY 4: Industrial Training & First Submission

- **Snowpark Push-down:** Perform all joins and aggregations inside Snowflake to keep local RAM free for XGBoost training
- **Hyperparameter "Safe Zone":**

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

- **Submit #1:** This is your "Pipe-Clean" submission. If you hit >0.30, you are on the right track.

---

## DAY 5: Tuning & Feature Pruning

- **Feature Importance Analysis:** Use `model.get_score(importance_type='gain')`. If a feature isn't in the top 15, consider dropping it to reduce noise.
- **Target-Specific Tuning:**
  - **Phosphorus** often requires more trees (`n_estimators`) because the signal is fainter
  - **Salinity** is often highly predictable; watch out for overfitting on small fluctuations
- **Submit #2:** Aiming for 0.40 – 0.43

---

## DAY 6: The "Sanity Check" & Error Analysis

- **Residual Plotting:** Plot `Predicted - Actual`. Are you consistently underestimating peaks?
  - _Fix:_ Add a "Rolling Standard Deviation" feature to capture volatility
- **Leakage Audit:** Double-check that no "future" data (like tomorrow's rainfall) accidentally leaked into today's training row
- **Submit #3:** This should be your "Stable" score

---

## DAY 7: Final Polish & Phase 2 Prep

- **Final Retrain:** Train on the _entire_ dataset (Train + Validation) using the best hyperparameters found
- **Documentation:** Start a bulleted list of your feature logic. _Why did you use NDWI? Why did you lag rainfall by 14 days?_ Crucial for Phase 2 Business Plan.
- **Final Submission:** Lock in your best model

---

## Key Strategic Notes

> **Complexity is a Trap:** A simple XGBoost model with brilliant features will always beat a complex Neural Network with poor features on this type of tabular data.

> **Snowflake is your Muscle:** Use SQL for the heavy math; use Python for the logic.

> **Feature signal wins, not hyperparameter squeezing.** Don't grid-search everything. Let early stopping do the work.

---

# DISCLAIMERS & RECOMMENDATIONS

## Verdict

- Windsurf + AI model is good enough to generate: Snowpark code, SQL feature pipelines, XGBoost training loops
- This roadmap can deliver a **working, competitive MVP in 7 days**
- It is **not "100% easy"** — but it is **low-risk and realistic**
- You are slightly over-professional for a first submission, which is fine as long as you **don't overbuild**

## What Is VERY Solid (Keep As-Is)

- Snowflake-first mindset
- RAW / STAGING / ANALYTICS schema separation
- 3 independent XGBoost models
- Time-based validation (non-negotiable)
- Feature-first > model-first thinking
- Early submissions ("pipe-clean" approach)

This aligns with: EY rules, scoring mechanics, small-data reality (~9,300 rows).

## Minor Corrections & Reality Checks

### 1. AI Model Usage — Use It Correctly

AI is excellent for scaffolding, but:

- **DO NOT** let it design your validation logic blindly
- **DO NOT** trust it with leakage-sensitive code without review
- **DO** use it for: Snowpark transformations, Feature SQL, XGBoost boilerplate, Plotting & diagnostics

> **Rule:** _If it touches time or joins → you review line by line._

### 2. Distance to Coast — Be Careful

- Derive from **public coastline shapefiles**
- Calculate **once**, store it
- Do **not** recompute per batch (wastes credits)
- Helps **Salinity**; may be neutral/noisy for **Phosphorus**
- Keep it **target-specific**, not global

### 3. Seasonal Encoding — Correct but Optional

- If short on time, rainfall lags matter more
- DOY helps smooth residuals, not create signal
- Use it **after** rainfall lags are working

### 4. Hyperparameters — Safe, But Don't Obsess

- `n_estimators=500` is fine
- Let **early stopping** do the work
- Do NOT grid-search everything
- You win by **feature signal**, not squeezing 0.01 R² from tuning

## GO / NO-GO Checklist

Before adding complexity, confirm ALL of these:

- [ ] You can reproduce the benchmark
- [ ] You understand why Lat/Lon can't be features
- [ ] You can explain every feature in plain English
- [ ] You submit early, even with mediocre scores
- [ ] You stop at "good enough" for week 1

**If any of these fail → slow down, don't add complexity.**

## Bottom Line

This roadmap is: Realistic, Professionally structured, Snowflake-efficient, MVP-ready in 7 days. It's **not flashy**, and that's why it works.
