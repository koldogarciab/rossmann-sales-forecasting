# Power BI data layer

Phase 7 generates a clean star-schema data layer for the Rossmann dashboard.

## Build the files

From the repository root:

```bash
python -m src.build_sql_model
```

The command creates these local files in `powerbi/data/`:

- `dim_date.csv`
- `dim_store.csv`
- `fact_sales_history.csv`
- `fact_sales_forecast.csv`
- `model_metrics.csv`
- `data_quality_results.csv`

The generated CSV files are ignored by Git because they can be rebuilt from the source data and code.

## Recommended Power BI relationships

- `dim_date[DateKey]` → `fact_sales_history[DateKey]` (1:*)
- `dim_date[DateKey]` → `fact_sales_forecast[DateKey]` (1:*)
- `dim_store[Store]` → `fact_sales_history[Store]` (1:*)
- `dim_store[Store]` → `fact_sales_forecast[Store]` (1:*)

Use single-direction filtering from each dimension to the fact tables. Mark `dim_date[Date]` as the date table and sort `MonthName` by `Month` and `DayName` by `DayOfWeek`.

## Fact-table grain

Both fact tables use one row per store and date. Historical sales and forecast sales remain separate, preventing actual and forecast measures from being mixed accidentally.
