# Phase 1 — Business Understanding and Data Audit Findings

## 1. Purpose

This phase assessed the structure, completeness, consistency, and modelling suitability of the original Rossmann Store Sales files before any cleaning, feature engineering, or model development.

The audit covered:

- File availability and dimensions
- Column structure and inferred data types
- Missing values
- Exact duplicates and key-level duplicates
- Dataset granularity
- Date validity and coverage
- Train/test schema differences
- Basic business-rule consistency
- Referential integrity
- Alignment between the test set and submission template

No raw data was modified during this phase.

---

## 2. Files audited

| Dataset | Rows | Columns | Purpose |
|---|---:|---:|---|
| `train.csv` | 1,017,209 | 9 | Historical daily sales and customer data |
| `store.csv` | 1,115 | 10 | Store-level descriptive attributes |
| `test.csv` | 41,088 | 8 | Future store-date combinations requiring forecasts |
| `sample_submission.csv` | 41,088 | 2 | Required Kaggle submission structure |

All four files were successfully loaded and none was empty or incomplete.

---

## 3. Confirmed data granularity

The expected business grain was confirmed:

- `train.csv`: one unique row per `Store` and `Date`
- `test.csv`: one unique row per `Store` and `Date`
- `store.csv`: one unique row per `Store`
- `test.csv`: one unique row per `Id`
- `sample_submission.csv`: one unique row per `Id`

No key-level duplicates were identified.

The principal prediction unit will therefore be:

> Daily sales for each store and forecast date.

---

## 4. Temporal coverage

### Historical period

- Start date: `2013-01-01`
- End date: `2015-07-31`
- Unique calendar dates: 942
- Missing dates in the overall historical calendar: 0

### Kaggle forecast period

- Start date: `2015-08-01`
- End date: `2015-09-17`
- Forecast horizon: 48 consecutive days
- Missing dates in the test calendar: 0

The test period begins immediately after the historical period, which is consistent with a forecasting use case.

All `Date` values were valid and all `DayOfWeek` values matched the corresponding calendar date.

Most stores contain the full 942-day history, although some stores have shorter records. The minimum observed store history was 758 days. This will require further investigation during the EDA.

---

## 5. Store coverage

- Historical data contains 1,115 stores.
- The test set contains 856 stores.
- All stores appearing in train and test exist in `store.csv`.
- 259 stores from the master table do not appear in the test set.

This is not treated as a data-quality error. The Kaggle test set simply requires predictions for a subset of historical stores.

---

## 6. Train/test schema comparison

### Columns only available in train

- `Sales`
- `Customers`

### Column only available in test

- `Id`

### Common columns

- `Store`
- `DayOfWeek`
- `Date`
- `Open`
- `Promo`
- `StateHoliday`
- `SchoolHoliday`

`Sales` is the prediction target.

`Customers` is available historically but not in the future test period. It would normally also be unknown when preparing a real operational sales forecast.

Therefore:

> `Customers` may be used for historical descriptive analysis, but it will not be used as a principal production predictor.

Using it directly would create a feature-availability problem and could produce misleading model performance.

---

## 7. Data types

Several variables require explicit treatment before modelling:

- `Date` is currently loaded as text and must be converted to a date type.
- `StateHoliday` is categorical and contains codes such as `0`, `a`, `b`, and `c`.
- `StoreType`, `Assortment`, and `PromoInterval` are categorical.
- `CompetitionDistance` and several competition and promotion date fields are stored as floating-point values because they contain missing values.
- `Open` is integer in train but floating-point in test because test contains missing values.

The only inferred type inconsistency between common train and test columns is `Open`.

---

## 8. Missing values

### `store.csv`

| Column | Missing values | Missing % |
|---|---:|---:|
| `Promo2SinceWeek` | 544 | 48.79% |
| `Promo2SinceYear` | 544 | 48.79% |
| `PromoInterval` | 544 | 48.79% |
| `CompetitionOpenSinceMonth` | 354 | 31.75% |
| `CompetitionOpenSinceYear` | 354 | 31.75% |
| `CompetitionDistance` | 3 | 0.27% |

### `test.csv`

| Column | Missing values | Missing % |
|---|---:|---:|
| `Open` | 11 | 0.03% |

There were no missing values in `train.csv` or `sample_submission.csv`.

### Interpretation

The 544 missing values in the Promo2-related fields correspond exactly to the 544 stores where `Promo2 = 0`.

These are structural missing values rather than conventional data-quality errors:

> A store that does not participate in Promo2 has no Promo2 start date or promotion interval.

The 354 missing competition opening dates may mean that the opening date is unknown or not applicable. Their treatment will be decided after further analysis.

The 11 missing `Open` values in the test set require an explicit forecasting rule before final predictions are generated.

---

## 9. Duplicate checks

No exact duplicate rows were identified in:

- `train.csv`
- `store.csv`
- `test.csv`
- `sample_submission.csv`

No duplicate business keys were identified.

---

## 10. Business-rule checks

The following controls passed:

- No negative sales values
- No negative customer values
- No records where `Open = 0` and `Sales != 0`
- No values outside the expected `{0, 1}` domain for `Open`
- No values outside the expected `{0, 1}` domain for `Promo`

Historical closed-store records are therefore consistent:

> When a store is marked as closed, historical sales are always zero.

However, 54 observations are marked as open while reporting zero sales.

These records may represent exceptional closures, data-entry issues, or genuine zero-sales days. They will be investigated during the EDA before any treatment decision is made.

---

## 11. Categorical domains

### Store type

- `a`
- `b`
- `c`
- `d`

Store type `a` is the most common, while type `b` is relatively rare.

### Assortment

- `a`
- `b`
- `c`

Assortment type `b` is highly underrepresented.

### State holiday

Train includes:

- `0`
- `a`
- `b`
- `c`

Test includes:

- `0`
- `a`

The absence of holiday types `b` and `c` in test is not considered an error. Those holiday categories simply do not occur during the 48-day test horizon.

### Promo2 interval

Observed patterns are:

- `Jan,Apr,Jul,Oct`
- `Feb,May,Aug,Nov`
- `Mar,Jun,Sept,Dec`

---

## 12. Test and submission alignment

The test set and submission template are fully aligned:

- Same number of rows: 41,088
- Same set of `Id` values
- Same `Id` order

Predictions can therefore be assigned directly to the `Sales` column of the submission template, provided that row order is preserved.

---

## 13. Initial modelling implications

The audit supports the following decisions:

1. Use `Sales` as the target variable.
2. Use one row per store and date as the modelling grain.
3. Preserve chronological order for validation.
4. Do not use a conventional random train/test split.
5. Exclude `Customers` from the principal production feature set.
6. Convert `Date` into a proper datetime type.
7. Treat Promo2 missing values as structural.
8. Investigate missing competition information before imputation.
9. Define a documented rule for the 11 missing `Open` values in test.
10. Treat closed-store sales as zero.
11. Investigate the 54 open-store zero-sales records.
12. Preserve the original Kaggle test set for final prediction generation rather than internal performance evaluation.

---

## 14. Open questions for the EDA

The next phase should investigate:

- Why some stores have shorter historical coverage
- Which stores contain the 54 open-but-zero-sales observations
- Whether the 3 missing competition distances follow a meaningful pattern
- How competition variables relate to sales
- Whether stores with missing competition dates behave differently
- How promotions affect sales by store type and assortment
- Sales patterns by weekday, month, year, and holiday
- Differences between stores included and excluded from the test set
- Whether extreme sales values represent genuine events or anomalies
- How closed days should be represented in model evaluation metrics

---

## 15. Phase conclusion

The Rossmann data is structurally strong and suitable for an end-to-end forecasting project.

No critical issues were found in file integrity, keys, duplicate records, dates, store references, or submission alignment.

The main preparation challenges are not severe data corruption issues, but business interpretation decisions:

- Feature availability at forecast time
- Structural missing values
- Closed-store treatment
- Exceptional open days with zero sales
- Store-level differences in historical coverage

These points will be addressed explicitly during the exploratory analysis and feature-engineering phases.