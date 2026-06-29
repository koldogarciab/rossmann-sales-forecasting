# Objetivos de validación — Power BI

Estos valores deben observarse sin filtros en el informe:

| Control | Valor esperado |
|---|---:|
| Forecast Sales | 247,034,117.42 |
| Forecast Rows | 41,088 |
| Forecast Stores | 856 |
| Forecast Dates | 48 |
| Forecast Open Store Days | 35,104 |
| Forecast Closed Store Days | 5,984 |
| Forecast Promo Store Days | 16,252 |
| Forecast Sales per Open Store Day | 7,037.2071 |
| Forecast Promo Sales | 132,852,876.66 |
| Forecast Non-Promo Sales | 114,181,240.76 |
| Forecast Promo Average | 8,174.5555 |
| Forecast Non-Promo Average | 6,056.7176 |
| Forecast Promo Uplift % | 34.9668% |
| Controls Status | 24/24 |
| Controls Failed | 0 |
| Mean RMSPE | 14.45% |
| RMSPE Standard Deviation | 0.88% |
| Kaggle Public RMSPE | 12.818% |
| Kaggle Private RMSPE | 14.556% |

## Controles de estructura

- `dim_date`: 990 filas.
- `dim_store`: 1,115 filas.
- `fact_sales_history`: 1,017,209 filas.
- `fact_sales_forecast`: 41,088 filas.
- Cuatro relaciones activas, uno a muchos y con filtro en una sola dirección.
- Cero relaciones entre las dos tablas de hechos.
- `model_metrics` y `data_quality_results` desconectadas.
