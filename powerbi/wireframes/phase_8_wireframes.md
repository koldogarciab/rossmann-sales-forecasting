# Wireframes del dashboard

## Page 1 — Executive Forecast

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Rossmann Sales Forecast | StoreType | Assortment | Promo2 | Date          │
├───────────────┬───────────────┬───────────────┬────────────────────────────┤
│ Forecast Sales│ Sales/Open Day│ Stores        │ Promo Uplift %             │
├───────────────────────────────────────────────┬────────────────────────────┤
│ Actual and Forecast Sales by Date             │ Forecast by Weekday        │
│                                               │                            │
├───────────────────────────────────────────────┼────────────────────────────┤
│ Forecast by Store Type                        │ StoreType × Assortment      │
└───────────────────────────────────────────────┴────────────────────────────┘
```

## Page 2 — Store Performance

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Store Performance | StoreType | Assortment | Promo2 | Store               │
├───────────────┬───────────────┬───────────────┬────────────────────────────┤
│ Top Store     │ Sales/Open Day│ Open Days     │ Closed Days                │
├───────────────────────────────────────────────┬────────────────────────────┤
│ Top 10 Stores                                 │ Competition Distance       │
│                                               │ vs Sales/Open Day          │
├────────────────────────────────────────────────────────────────────────────┤
│ Detailed Store Table                                                       │
└────────────────────────────────────────────────────────────────────────────┘
```

## Page 3 — Promotion & Calendar

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Promotion & Calendar | StoreType | Assortment | Date                       │
├───────────────┬───────────────┬───────────────┬────────────────────────────┤
│ Promo Sales   │ Non-Promo Sales│ Promo Average │ Promo Uplift %            │
├───────────────────────────────────────────────┬────────────────────────────┤
│ Promo vs Non-Promo Average by Weekday         │ Sales and Promo Days       │
├───────────────────────────────────────────────┼────────────────────────────┤
│ Forecast by State Holiday                     │ Weekday × Promo Matrix      │
└───────────────────────────────────────────────┴────────────────────────────┘
```

## Page 4 — Model & Data Quality

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Model & Data Quality                                                       │
├────────────┬────────────┬────────────┬────────────┬────────────────────────┤
│ Mean RMSPE │ Std Dev    │ Public     │ Private    │ Controls 24/24         │
├───────────────────────────────────────────────┬────────────────────────────┤
│ Data Quality Control Table                    │ Model Metadata             │
├───────────────────────────────────────────────┴────────────────────────────┤
│ Methodology and validation notes                                           │
└────────────────────────────────────────────────────────────────────────────┘
```
