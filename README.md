# Rossmann Retail Sales Forecasting & FP&A Analytics

An end-to-end forecasting project that predicts daily sales for each Rossmann store and translates the results into operational and FP&A insights through Python, SQL and Power BI.

![Executive forecast dashboard](reports/figures/dashboard/executive_forecast.png)

## Executive summary

The project forecasts sales for **856 stores across a 48-day horizon** from **1 August to 17 September 2015**. The selected model is a transparent recent-history benchmark based on the previous 365 days, segmented by store, weekday and promotion status.

### Final results

| Metric | Result |
|---|---:|
| Forecast sales | 247,034,117.42 |
| Forecast rows | 41,088 |
| Forecast stores | 856 |
| Open store days | 35,104 |
| Mean RMSPE across three temporal folds | 14.45% |
| RMSPE standard deviation | 0.88% |
| Kaggle public RMSPE | 12.818% |
| Kaggle private RMSPE | 14.556% |
| Data-quality controls passed | 24 / 24 |

The Kaggle private score was almost identical to the mean temporal backtest, providing an external confirmation that the validation design was representative.

## Business problem

Rossmann store managers need a reliable forward view of store sales to support workforce planning, promotion analysis, cash-flow forecasting and management reporting. The prediction unit is **daily sales by store and date**.

The project answers four practical questions:

1. How much is expected to be sold during the next 48 days?
2. Which stores, weekdays and formats account for the forecast?
3. How does the forecast differ between promotional and non-promotional store days?
4. How reliable is the model and how could it be operated in production?

## Data

The project uses the public Rossmann Store Sales competition data:

- `train.csv`: 1,017,209 historical store-date records.
- `store.csv`: master data for 1,115 stores.
- `test.csv`: 41,088 future store-date records for 856 stores.
- `sample_submission.csv`: required Kaggle output structure.

Raw competition files are not intended to be distributed through the repository. See `data/raw/README.md` for download instructions.

## End-to-end architecture

![Project architecture](reports/figures/project_architecture.png)

The solution combines:

- auditable data-quality controls;
- leakage-safe feature engineering;
- chronological validation;
- model comparison and stability analysis;
- final batch scoring;
- SQL analytical modelling;
- an interactive Power BI dashboard;
- conceptual monitoring and retraining design.

## Data audit and preparation

The audit confirmed one row per store and date, continuous calendar coverage and valid referential integrity. The main preparation decisions were:

- `Sales` is the target.
- `Customers` is excluded as a production predictor because it is absent from the test set and would normally be unknown at forecast time.
- Validation is chronological rather than random.
- The original Kaggle test is reserved for final scoring.
- The 11 missing `Open` values for Store 622 are imputed as open, with an explicit traceability flag.
- Closed stores receive a forecast of zero.

Feature engineering covers calendar patterns, store characteristics, competition, Promo2 activity and forecast-availability controls.

## Validation strategy

A single holdout can favour a model by chance, so the final model comparison uses **three consecutive 48-day temporal folds**, each restricted to the same 856 stores required by the Kaggle test.

The primary metric is **RMSPE**, supported by MAE, RMSE, WAPE and bias. RMSPE is aligned with the competition and measures proportional forecasting error across stores with different sales levels.

## Models evaluated

The project compares transparent historical averages and machine-learning alternatives:

- global open-store mean;
- store mean;
- store + weekday mean;
- store + weekday + promotion mean;
- Ridge regression on direct and log-transformed sales;
- target-encoded HistGradientBoosting on direct and log-transformed sales;
- 180-day and 365-day recent-history variants;
- residual boosting and baseline-residual blends.

The best Phase 4 baseline was `Store + weekday + Promo`, with an RMSPE of approximately 0.1449 on the final holdout.

## Final model selection

The selected production model is:

> **Recent 365-day Store + weekday + Promo**

For each open-store forecast row, the model uses the recent historical mean for the matching store, weekday and promotion status. If the exact combination is unavailable, it falls back to:

1. store + weekday;
2. store;
3. global open-store mean.

A 50% baseline / 50% residual blend achieved a marginally lower mean RMSPE of 0.1442, but it was not selected because its fold-to-fold variability was higher. The chosen model won two of the three folds and performed best on the final fold.

## Explainability

The final model is intrinsically interpretable rather than a black box. Every forecast can be traced to a recent historical peer group and a documented fallback level.

The main forecast drivers are directly observable:

- **Store** captures persistent local demand patterns.
- **Weekday** captures the weekly operating cycle.
- **Promotion** separates promoted and non-promoted store days.
- **Open status** is a hard business rule that sets closed-store forecasts to zero.

The forecasted average per open store day is approximately **8,175 under promotion** and **6,057 without promotion**, an uplift of about **35.0%**. This is a descriptive forecast comparison, not a causal estimate of promotion effectiveness.

![Promotion effect](reports/figures/phase9_promo_effect.png)

Further explainability and business-impact analysis is available in `notebooks/09_explainability_business_impact.ipynb`.

## Business results

The final forecast totals **247.03 million** across the 48-day horizon.

Key planning insights include:

- promotional store days account for approximately 53.8% of forecast sales while representing about 46.3% of open store days;
- Monday has the highest total forecast and the highest average sales per open store day;
- the top store is Store 262, with approximately 997,985 in forecast sales;
- the top 10 stores account for about 3.16% of the total, indicating that sales are distributed across a broad store network rather than dominated by a small number of locations.

## Power BI dashboard

The analytical model is presented in four Power BI pages:

### 1. Executive Forecast

![Executive Forecast](reports/figures/dashboard/executive_forecast.png)

### 2. Store Performance

![Store Performance](reports/figures/dashboard/store_performance.png)

### 3. Promotion & Calendar

![Promotion and Calendar](reports/figures/dashboard/promotion_calendar.png)

### 4. Model & Data Quality

![Model and Data Quality](reports/figures/dashboard/model_data_quality.png)

The report is stored at `powerbi/rossmann_sales_forecast_dashboard.pbix`.

## SQL analytical model

Phase 7 creates a SQLite analytical database and Power BI-ready exports. The star schema contains:

- `dim_date`;
- `dim_store`;
- `fact_sales_history`;
- `fact_sales_forecast`;
- `model_metrics`;
- `data_quality_results`.

The build process runs 24 population, integrity, business-rule and reconciliation controls.

## Conceptual production design

The model is best deployed as a **batch forecasting process**, because store planning is performed over a multi-week horizon rather than through individual real-time requests.

A realistic operating design would:

1. ingest daily sales, store master data, opening status and promotion plans;
2. run schema, completeness and referential-integrity checks;
3. rebuild the rolling 365-day historical aggregates;
4. produce a refreshed six-week forecast on a weekly planning cycle;
5. publish versioned outputs to the analytical database and Power BI;
6. compare forecasts with actuals as they arrive.

The model could be reviewed monthly and retrained when either:

- rolling RMSPE or WAPE deteriorates materially;
- bias becomes persistent;
- store, promotion or opening patterns drift;
- new stores or material business changes appear.

See `docs/phase_9_production_design_ES.md` for the detailed monitoring and versioning proposal.

## Reproducibility

Create the environment:

```bash
conda env create -f environment.yml
conda activate rossmann-forecasting
python -m ipykernel install --user --name rossmann-forecasting --display-name "Python (rossmann-forecasting)"
```

Run the notebooks in order:

```text
01_data_audit.ipynb
02_eda.ipynb
03_feature_engineering.ipynb
04_baseline_models.ipynb
05_model_improvement.ipynb
06_final_forecast_submission.ipynb
07_sql_data_model.ipynb
09_explainability_business_impact.ipynb
```

Build the SQL model from the repository root:

```bash
python -m src.build_sql_model
```

The main final outputs are:

```text
reports/submissions/rossmann_submission_recent365.csv
reports/tables/final_test_forecast.csv
models/final_model_metadata.json
data/processed/rossmann_analytics.db
powerbi/rossmann_sales_forecast_dashboard.pbix
```

## Repository structure

```text
data/          raw, interim and processed data locations
docs/          phase guides, decisions and production design
models/        final model metadata
notebooks/     reproducible analytical workflow
powerbi/       dashboard, theme and DAX measures
reports/       figures, tables and Kaggle submission
sql/           table, view, analysis and quality-control SQL
src/           reusable feature, metric, forecast and SQL-build modules
```

## Limitations and next steps

- The dataset does not contain prices, product mix, local weather or external events.
- The promotion comparison is descriptive rather than causal.
- Store identity captures local demand but does not explain the underlying socioeconomic factors.
- New stores with little history would depend more heavily on fallback rules.
- A future challenger could combine the transparent baseline with a more stable residual model and use SHAP or permutation importance.
- Prediction intervals and scenario forecasts would improve planning under uncertainty.

## Conclusion

The project demonstrates an end-to-end forecasting workflow that prioritises temporal validity, reproducibility and business usability. The final model is deliberately transparent and stable, the external Kaggle result confirms the internal validation, and the SQL/Power BI layer converts row-level predictions into an auditable planning product.
