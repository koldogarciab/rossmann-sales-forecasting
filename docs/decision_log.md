# Decision Log

## DL-001 — Prediction unit
- **Decision:** Daily sales by store and date.
- **Reason:** This matches the source data granularity and the operational planning use case.
- **Status:** Initial; to be confirmed after the data audit.

## DL-002 — Target variable
- **Decision:** `Sales`.
- **Reason:** It is the business outcome to forecast.
- **Status:** Confirmed by project scope.

## DL-003 — Treatment of `Customers`
- **Decision:** Do not use `Customers` as a principal production predictor.
- **Reason:** It is absent from the Kaggle test set and would normally be unknown at forecast creation time.
- **Permitted use:** Historical descriptive analysis, with explicit documentation.
- **Risk controlled:** Data leakage / unavailable-at-inference feature.

## DL-004 — Validation approach
- **Decision:** Use chronological train/validation/test splits rather than a conventional random split.
- **Reason:** The project is a forecasting problem and must simulate prediction of future periods.
- **Status:** Split dates will be selected after the audit and EDA.

## DL-005 — Kaggle test set
- **Decision:** Reserve the original Kaggle test set for final forecast generation.
- **Reason:** It has no observed `Sales`, so it cannot replace an internal evaluation period.
- **Status:** Confirmed.

## DL-006 — Raw data governance
- **Decision:** Exclude original CSV files from Git.
- **Reason:** Avoid repository bloat and respect dataset distribution conditions.
- **Implementation:** `data/raw/` is ignored except for documentation placeholders.

## DL-007 — Initial environment
- **Decision:** Python 3.11 with a minimal Phase 0-2 dependency set.
- **Reason:** Keep installation stable and avoid adding libraries before they are needed.
- **Later additions:** SHAP, database connectors, and other packages will be introduced in the phase where they are used.
