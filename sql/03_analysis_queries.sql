-- Phase 7: example analytical queries for SQLite
-- Each query can be executed independently.

-- 1. Database overview and table coverage
SELECT 'Historical fact' AS Dataset,
       COUNT(*) AS Rows,
       COUNT(DISTINCT Store) AS Stores,
       MIN(d.Date) AS StartDate,
       MAX(d.Date) AS EndDate
FROM fact_sales_history h
JOIN dim_date d ON d.DateKey = h.DateKey
UNION ALL
SELECT 'Forecast fact',
       COUNT(*),
       COUNT(DISTINCT Store),
       MIN(d.Date),
       MAX(d.Date)
FROM fact_sales_forecast f
JOIN dim_date d ON d.DateKey = f.DateKey;

-- 2. Monthly historical performance on open store-days
SELECT d.Year,
       d.Month,
       d.MonthName,
       SUM(h.Sales) AS Sales,
       SUM(h.Customers) AS Customers,
       SUM(h.Open) AS OpenStoreDays,
       SUM(h.OpenPromoFlag) AS PromoStoreDays,
       CASE WHEN SUM(h.Open) = 0 THEN NULL ELSE SUM(h.Sales) * 1.0 / SUM(h.Open) END AS SalesPerOpenStoreDay,
       CASE WHEN SUM(h.Customers) = 0 THEN NULL ELSE SUM(h.Sales) * 1.0 / SUM(h.Customers) END AS SalesPerCustomer
FROM fact_sales_history h
JOIN dim_date d ON d.DateKey = h.DateKey
GROUP BY d.Year, d.Month, d.MonthName
ORDER BY d.Year, d.Month;

-- 3. Continuous actual and forecast daily timeline
SELECT Date,
       Scenario,
       ReportingStores,
       OpenStores,
       PromoStoreDays,
       Sales,
       MeanSalesPerOpenStore
FROM vw_daily_sales_timeline
ORDER BY Date, Scenario;

-- 4. Forecast by store type and assortment
SELECT StoreType,
       Assortment,
       Stores,
       OpenStoreDays,
       PromoStoreDays,
       ForecastSales,
       MeanSalesPerOpenStoreDay
FROM vw_forecast_by_store_type
ORDER BY ForecastSales DESC;

-- 5. Forecast with and without promotion
SELECT Promo,
       OpenStoreDays,
       ForecastSales,
       MeanSales
FROM vw_forecast_promo_summary
ORDER BY Promo;

-- 6. Top 20 stores by total forecast sales
SELECT Store,
       StoreType,
       Assortment,
       ForecastSales,
       OpenDays,
       PromoDays,
       ClosedDays,
       MeanSalesPerOpenDay
FROM vw_forecast_store_summary
ORDER BY ForecastSales DESC
LIMIT 20;

-- 7. Forecast profile by weekday
SELECT DayOfWeek,
       DayName,
       Stores,
       OpenStoreDays,
       PromoStoreDays,
       ForecastSales,
       MeanSalesPerOpenStore
FROM vw_forecast_weekday_summary
ORDER BY DayOfWeek;

-- 8. Stores with the largest promotion exposure during the forecast horizon
SELECT Store,
       StoreType,
       Assortment,
       PromoDays,
       OpenDays,
       ROUND(PromoDays * 1.0 / NULLIF(OpenDays, 0), 4) AS PromoShareOfOpenDays,
       ForecastSales
FROM vw_forecast_store_summary
WHERE OpenDays > 0
ORDER BY PromoShareOfOpenDays DESC, ForecastSales DESC
LIMIT 25;

-- 9. Model performance and forecast scope
SELECT ModelName,
       ModelType,
       HistoryWindowDays,
       HistoricalDataStart,
       ModelLookbackStart,
       HistoricalDataEnd,
       ForecastStart,
       ForecastEnd,
       MeanRMSPE,
       RMSPEStandardDeviation,
       KagglePublicRMSPE,
       KagglePrivateRMSPE,
       ForecastTotalSales
FROM model_metrics;

-- 10. Data-quality status
SELECT Area,
       ControlName,
       Passed,
       ObservedValue,
       ExpectedValue,
       Tolerance,
       CheckedAtUTC
FROM data_quality_results
ORDER BY Passed, Area, CheckId;
