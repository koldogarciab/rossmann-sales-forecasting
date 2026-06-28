-- Phase 7: reusable analytical views
-- SQLite dialect

CREATE VIEW vw_sales_timeline AS
SELECT
    h.DateKey,
    d.Date,
    h.Store,
    'Actual' AS Scenario,
    h.Sales,
    h.Customers,
    h.Open,
    h.Promo,
    h.OpenPromoFlag,
    h.StateHoliday,
    h.SchoolHoliday,
    NULL AS ModelName
FROM fact_sales_history h
JOIN dim_date d ON d.DateKey = h.DateKey

UNION ALL

SELECT
    f.DateKey,
    d.Date,
    f.Store,
    'Forecast' AS Scenario,
    f.ForecastSales AS Sales,
    NULL AS Customers,
    f.OpenFilled AS Open,
    f.Promo,
    f.OpenPromoFlag,
    f.StateHoliday,
    f.SchoolHoliday,
    f.ModelName
FROM fact_sales_forecast f
JOIN dim_date d ON d.DateKey = f.DateKey;

CREATE VIEW vw_daily_sales_timeline AS
SELECT
    DateKey,
    Date,
    Scenario,
    COUNT(*) AS ReportingStores,
    SUM(Open) AS OpenStores,
    SUM(OpenPromoFlag) AS PromoStoreDays,
    SUM(Sales) AS Sales,
    CASE WHEN SUM(Open) = 0 THEN NULL ELSE SUM(Sales) * 1.0 / SUM(Open) END AS MeanSalesPerOpenStore
FROM vw_sales_timeline
GROUP BY DateKey, Date, Scenario;

CREATE VIEW vw_forecast_daily_summary AS
SELECT
    f.DateKey,
    d.Date,
    COUNT(*) AS ReportingStores,
    SUM(f.OpenFilled) AS OpenStores,
    SUM(f.OpenPromoFlag) AS PromoStoreDays,
    SUM(f.ForecastSales) AS ForecastSales,
    CASE WHEN SUM(f.OpenFilled) = 0 THEN NULL
         ELSE SUM(f.ForecastSales) * 1.0 / SUM(f.OpenFilled)
    END AS MeanSalesPerOpenStore
FROM fact_sales_forecast f
JOIN dim_date d ON d.DateKey = f.DateKey
GROUP BY f.DateKey, d.Date;

CREATE VIEW vw_forecast_store_summary AS
SELECT
    f.Store,
    s.StoreType,
    s.Assortment,
    s.Promo2,
    SUM(f.ForecastSales) AS ForecastSales,
    SUM(f.OpenFilled) AS OpenDays,
    SUM(f.OpenPromoFlag) AS PromoDays,
    AVG(f.ForecastSales) AS MeanCalendarDaySales,
    MAX(f.ForecastSales) AS MaximumDailySales,
    SUM(CASE WHEN f.OpenFilled = 0 THEN 1 ELSE 0 END) AS ClosedDays,
    CASE WHEN SUM(f.OpenFilled) = 0 THEN NULL
         ELSE SUM(f.ForecastSales) * 1.0 / SUM(f.OpenFilled)
    END AS MeanSalesPerOpenDay
FROM fact_sales_forecast f
JOIN dim_store s ON s.Store = f.Store
GROUP BY f.Store, s.StoreType, s.Assortment, s.Promo2;

CREATE VIEW vw_forecast_weekday_summary AS
SELECT
    d.DayOfWeek,
    d.DayName,
    COUNT(*) AS Rows,
    COUNT(DISTINCT f.Store) AS Stores,
    SUM(f.ForecastSales) AS ForecastSales,
    SUM(f.OpenFilled) AS OpenStoreDays,
    SUM(f.OpenPromoFlag) AS PromoStoreDays,
    CASE WHEN SUM(f.OpenFilled) = 0 THEN NULL
         ELSE SUM(f.ForecastSales) * 1.0 / SUM(f.OpenFilled)
    END AS MeanSalesPerOpenStore
FROM fact_sales_forecast f
JOIN dim_date d ON d.DateKey = f.DateKey
GROUP BY d.DayOfWeek, d.DayName;

CREATE VIEW vw_forecast_promo_summary AS
SELECT
    f.Promo,
    SUM(f.OpenFilled) AS OpenStoreDays,
    SUM(f.ForecastSales) AS ForecastSales,
    CASE WHEN SUM(f.OpenFilled) = 0 THEN NULL
         ELSE SUM(f.ForecastSales) * 1.0 / SUM(f.OpenFilled)
    END AS MeanSales
FROM fact_sales_forecast f
GROUP BY f.Promo;

CREATE VIEW vw_forecast_by_store_type AS
SELECT
    s.StoreType,
    s.Assortment,
    COUNT(DISTINCT f.Store) AS Stores,
    SUM(f.OpenFilled) AS OpenStoreDays,
    SUM(f.OpenPromoFlag) AS PromoStoreDays,
    SUM(f.ForecastSales) AS ForecastSales,
    CASE WHEN SUM(f.OpenFilled) = 0 THEN NULL
         ELSE SUM(f.ForecastSales) * 1.0 / SUM(f.OpenFilled)
    END AS MeanSalesPerOpenStoreDay
FROM fact_sales_forecast f
JOIN dim_store s ON s.Store = f.Store
GROUP BY s.StoreType, s.Assortment;
