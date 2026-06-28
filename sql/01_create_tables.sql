-- Phase 7: analytical star schema for Rossmann sales forecasting
-- SQLite dialect

PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS vw_forecast_by_store_type;
DROP VIEW IF EXISTS vw_forecast_promo_summary;
DROP VIEW IF EXISTS vw_forecast_weekday_summary;
DROP VIEW IF EXISTS vw_forecast_store_summary;
DROP VIEW IF EXISTS vw_forecast_daily_summary;
DROP VIEW IF EXISTS vw_daily_sales_timeline;
DROP VIEW IF EXISTS vw_sales_timeline;

DROP TABLE IF EXISTS data_quality_results;
DROP TABLE IF EXISTS model_metrics;
DROP TABLE IF EXISTS fact_sales_forecast;
DROP TABLE IF EXISTS fact_sales_history;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    DateKey        INTEGER PRIMARY KEY,
    Date           TEXT NOT NULL UNIQUE,
    Year           INTEGER NOT NULL,
    Quarter        INTEGER NOT NULL,
    QuarterLabel   TEXT NOT NULL,
    Month          INTEGER NOT NULL,
    MonthName      TEXT NOT NULL,
    YearMonth      TEXT NOT NULL,
    ISOWeek        INTEGER NOT NULL,
    DayOfMonth     INTEGER NOT NULL,
    DayOfWeek      INTEGER NOT NULL CHECK (DayOfWeek BETWEEN 1 AND 7),
    DayName        TEXT NOT NULL,
    IsWeekend      INTEGER NOT NULL CHECK (IsWeekend IN (0, 1))
);

CREATE TABLE dim_store (
    Store                       INTEGER PRIMARY KEY,
    StoreType                   TEXT,
    Assortment                  TEXT,
    CompetitionDistance         REAL,
    CompetitionOpenSinceMonth   INTEGER,
    CompetitionOpenSinceYear    INTEGER,
    CompetitionOpenDate         TEXT,
    Promo2                      INTEGER NOT NULL CHECK (Promo2 IN (0, 1)),
    Promo2SinceWeek             INTEGER,
    Promo2SinceYear             INTEGER,
    Promo2StartDate             TEXT,
    PromoInterval               TEXT
);

CREATE TABLE fact_sales_history (
    Store            INTEGER NOT NULL,
    DateKey          INTEGER NOT NULL,
    Sales            REAL NOT NULL CHECK (Sales >= 0),
    Customers        INTEGER NOT NULL CHECK (Customers >= 0),
    Open             INTEGER NOT NULL CHECK (Open IN (0, 1)),
    Promo            INTEGER NOT NULL CHECK (Promo IN (0, 1)),
    OpenPromoFlag    INTEGER NOT NULL CHECK (OpenPromoFlag IN (0, 1)),
    StateHoliday     TEXT NOT NULL,
    SchoolHoliday    INTEGER NOT NULL CHECK (SchoolHoliday IN (0, 1)),
    PRIMARY KEY (Store, DateKey),
    FOREIGN KEY (Store) REFERENCES dim_store(Store),
    FOREIGN KEY (DateKey) REFERENCES dim_date(DateKey)
);

CREATE TABLE fact_sales_forecast (
    Id                 INTEGER PRIMARY KEY,
    Store              INTEGER NOT NULL,
    DateKey            INTEGER NOT NULL,
    OpenOriginal       REAL,
    OpenFilled         INTEGER NOT NULL CHECK (OpenFilled IN (0, 1)),
    OpenMissingFlag    INTEGER NOT NULL CHECK (OpenMissingFlag IN (0, 1)),
    Promo              INTEGER NOT NULL CHECK (Promo IN (0, 1)),
    OpenPromoFlag      INTEGER NOT NULL CHECK (OpenPromoFlag IN (0, 1)),
    StateHoliday       TEXT NOT NULL,
    SchoolHoliday      INTEGER NOT NULL CHECK (SchoolHoliday IN (0, 1)),
    Promo2Active       INTEGER NOT NULL CHECK (Promo2Active IN (0, 1)),
    BaselineRecent365  REAL NOT NULL CHECK (BaselineRecent365 >= 0),
    ForecastSales      REAL NOT NULL CHECK (ForecastSales >= 0),
    ModelName          TEXT NOT NULL,
    UNIQUE (Store, DateKey),
    FOREIGN KEY (Store) REFERENCES dim_store(Store),
    FOREIGN KEY (DateKey) REFERENCES dim_date(DateKey)
);

CREATE TABLE model_metrics (
    ModelKey                 INTEGER PRIMARY KEY CHECK (ModelKey = 1),
    Project                  TEXT NOT NULL,
    ModelName                TEXT NOT NULL,
    ModelType                TEXT NOT NULL,
    PredictionColumn         TEXT NOT NULL,
    HistoryWindowDays        INTEGER NOT NULL,
    HistoricalDataStart      TEXT NOT NULL,
    HistoricalDataEnd        TEXT NOT NULL,
    ModelLookbackStart       TEXT NOT NULL,
    ForecastStart            TEXT NOT NULL,
    ForecastEnd              TEXT NOT NULL,
    ForecastRows             INTEGER NOT NULL,
    ForecastStores           INTEGER NOT NULL,
    ForecastDates            INTEGER NOT NULL,
    OpenStoreDays            INTEGER NOT NULL,
    ClosedStoreDays          INTEGER NOT NULL,
    MissingOpenValues        INTEGER NOT NULL,
    ForecastTotalSales       REAL NOT NULL,
    MeanRMSPE                REAL NOT NULL,
    RMSPEStandardDeviation   REAL NOT NULL,
    FinalFoldRMSPE           REAL NOT NULL,
    KagglePublicRMSPE        REAL NOT NULL,
    KagglePrivateRMSPE       REAL NOT NULL,
    GeneratedAtUTC           TEXT NOT NULL,
    KaggleEvaluatedAtUTC     TEXT,
    SelectionReason          TEXT NOT NULL,
    ClosedStoreRule          TEXT NOT NULL,
    MissingOpenRule          TEXT NOT NULL
);

CREATE TABLE data_quality_results (
    CheckId          INTEGER PRIMARY KEY AUTOINCREMENT,
    Area             TEXT NOT NULL,
    ControlName      TEXT NOT NULL,
    Passed           INTEGER NOT NULL CHECK (Passed IN (0, 1)),
    ObservedValue    TEXT,
    ExpectedValue    TEXT,
    Tolerance        TEXT,
    CheckedAtUTC     TEXT NOT NULL
);
