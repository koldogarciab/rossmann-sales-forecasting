-- Phase 7: SQL data-quality checks
-- A result of zero in the issue-count queries means the control passes.

-- 1. Duplicate historical Store-Date keys
SELECT COUNT(*) AS DuplicateHistoricalKeys
FROM (
    SELECT Store, DateKey
    FROM fact_sales_history
    GROUP BY Store, DateKey
    HAVING COUNT(*) > 1
);

-- 2. Duplicate forecast Store-Date keys
SELECT COUNT(*) AS DuplicateForecastKeys
FROM (
    SELECT Store, DateKey
    FROM fact_sales_forecast
    GROUP BY Store, DateKey
    HAVING COUNT(*) > 1
);

-- 3. Historical records without a store dimension
SELECT COUNT(*) AS HistoricalStoreOrphans
FROM fact_sales_history h
LEFT JOIN dim_store s ON s.Store = h.Store
WHERE s.Store IS NULL;

-- 4. Forecast records without a store dimension
SELECT COUNT(*) AS ForecastStoreOrphans
FROM fact_sales_forecast f
LEFT JOIN dim_store s ON s.Store = f.Store
WHERE s.Store IS NULL;

-- 5. Records without a date dimension
SELECT
    (SELECT COUNT(*)
     FROM fact_sales_history h
     LEFT JOIN dim_date d ON d.DateKey = h.DateKey
     WHERE d.DateKey IS NULL)
    +
    (SELECT COUNT(*)
     FROM fact_sales_forecast f
     LEFT JOIN dim_date d ON d.DateKey = f.DateKey
     WHERE d.DateKey IS NULL) AS DateOrphans;

-- 6. Closed stores with a non-zero forecast
SELECT COUNT(*) AS ClosedStoreNonZeroForecasts
FROM fact_sales_forecast
WHERE OpenFilled = 0 AND ABS(ForecastSales) > 0.000001;

-- 7. Inconsistent OpenPromoFlag in both fact tables
SELECT
    (SELECT COUNT(*) FROM fact_sales_history
     WHERE OpenPromoFlag <> CASE WHEN Open = 1 AND Promo = 1 THEN 1 ELSE 0 END)
    +
    (SELECT COUNT(*) FROM fact_sales_forecast
     WHERE OpenPromoFlag <> CASE WHEN OpenFilled = 1 AND Promo = 1 THEN 1 ELSE 0 END)
    AS OpenPromoFlagMismatches;

-- 8. Missing or negative measures
SELECT
    SUM(CASE WHEN ForecastSales IS NULL THEN 1 ELSE 0 END) AS MissingForecasts,
    SUM(CASE WHEN ForecastSales < 0 THEN 1 ELSE 0 END) AS NegativeForecasts
FROM fact_sales_forecast;

-- 9. Forecast population
SELECT COUNT(*) AS ForecastRows,
       COUNT(DISTINCT Store) AS ForecastStores,
       COUNT(DISTINCT DateKey) AS ForecastDates,
       SUM(OpenMissingFlag) AS ImputedOpenValues
FROM fact_sales_forecast;

-- 10. Forecast totals by source of aggregation
SELECT
    (SELECT ROUND(SUM(ForecastSales), 6) FROM fact_sales_forecast) AS FactTotal,
    (SELECT ROUND(SUM(ForecastSales), 6) FROM vw_forecast_daily_summary) AS DailyViewTotal,
    (SELECT ROUND(SUM(ForecastSales), 6) FROM vw_forecast_store_summary) AS StoreViewTotal;
