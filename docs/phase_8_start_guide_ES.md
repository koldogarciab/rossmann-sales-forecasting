# Fase 8 — Dashboard de Power BI

## Objetivo

Construir un dashboard profesional y reproducible sobre la capa analítica creada en la Fase 7. El informe estará orientado a portfolio y combinará tres perspectivas:

1. previsión ejecutiva de ventas;
2. análisis operativo por tienda, promoción y calendario;
3. validación del modelo y calidad del dato.

El dashboard se redactará en inglés para que pueda utilizarse en candidaturas y entrevistas en Australia. Las notas técnicas y la explicación de la fase se mantendrán en castellano.

## Fuente de datos

Ejecutar antes de abrir Power BI:

```bash
python -m src.build_sql_model
```

Power BI importará individualmente estos seis CSV desde `powerbi/data/`:

- `dim_date.csv`
- `dim_store.csv`
- `fact_sales_history.csv`
- `fact_sales_forecast.csv`
- `model_metrics.csv`
- `data_quality_results.csv`

No combinar los CSV mediante el conector de carpeta: tienen esquemas y funciones diferentes.

## Modelo semántico esperado

Relaciones activas, uno a muchos y con dirección de filtro única:

- `dim_date[DateKey]` → `fact_sales_history[DateKey]`
- `dim_date[DateKey]` → `fact_sales_forecast[DateKey]`
- `dim_store[Store]` → `fact_sales_history[Store]`
- `dim_store[Store]` → `fact_sales_forecast[Store]`

`model_metrics` y `data_quality_results` permanecerán sin relaciones. No relacionar las dos tablas de hechos entre sí.

## Entregable

Guardar el informe como:

```text
powerbi/rossmann_sales_forecasting_dashboard.pbix
```

Antes del commit se revisarán:

- relaciones y tipos de datos;
- medidas DAX;
- totales de reconciliación;
- filtros e interacciones;
- consistencia visual;
- ausencia de archivos temporales.
