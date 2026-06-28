# Fase 7 — Modelo de datos, SQLite y capa analítica para Power BI

## Objetivo

Transformar los datos históricos y el forecast final de la Fase 6 en una capa analítica reproducible. La fase crea un modelo en estrella, una base SQLite, consultas SQL reutilizables y tablas CSV preparadas para Power BI.

La granularidad principal de las dos tablas de hechos es **una fila por tienda y fecha**.

## Archivos incorporados

```text
notebooks/07\_sql\_data\_model.ipynb
src/build\_sql\_model.py
sql/01\_create\_tables.sql
sql/02\_create\_views.sql
sql/03\_analysis\_queries.sql
sql/04\_data\_quality\_checks.sql
docs/phase\_7\_start\_guide\_ES.md
docs/phase\_7\_data\_dictionary\_ES.md
powerbi/README.md
powerbi/data/.gitkeep
```

También se actualiza `.gitignore` para excluir los CSV generados dentro de `powerbi/data/`.

## Salidas generadas localmente

```text
data/processed/rossmann\_analytics.db
powerbi/data/dim\_date.csv
powerbi/data/dim\_store.csv
powerbi/data/fact\_sales\_history.csv
powerbi/data/fact\_sales\_forecast.csv
powerbi/data/model\_metrics.csv
powerbi/data/data\_quality\_results.csv
```

Estas salidas se reconstruyen mediante código y no deben subirse al repositorio.

## Ejecución recomendada

Desde la raíz del repositorio:

```bash
python -m src.build\_sql\_model
```

También puede ejecutarse el notebook `notebooks/07\_sql\_data\_model.ipynb`, que llama a la misma lógica y muestra los controles y consultas de revisión.

## Resultado esperado en la terminal

El mensaje final debe incluir:

```text
Phase 7 analytical model created successfully.
Controls passed: 24/24
Forecast rows: 41,088
Forecast stores: 856
```

El total de forecast se mostrará con decimales y debe coincidir con la Fase 6.

## Revisión antes del commit

No hacer commit todavía. Primero revisar:

1. que los 24 controles estén aprobados;
2. que `rossmann\_analytics.db` exista en `data/processed/`;
3. que existan los seis CSV dentro de `powerbi/data/`;
4. que las consultas del notebook devuelvan 1.017.209 filas históricas y 41.088 filas de forecast;
5. que haya 1.115 tiendas en `dim\_store` y 856 tiendas en el forecast;
6. que las tiendas cerradas tengan forecast cero;
7. que el total de forecast coincida con los informes de la Fase 6.

## Estructura analítica

* `dim\_date` y `dim\_store` contienen los atributos descriptivos.
* `fact\_sales\_history` contiene ventas y clientes reales.
* `fact\_sales\_forecast` contiene las predicciones finales y las variables del horizonte de Kaggle.
* `model\_metrics` documenta el modelo, el backtest y los resultados de Kaggle.
* `data\_quality\_results` conserva el resultado de los controles ejecutados.

Las tablas agregadas de la Fase 6 se utilizan como controles de reconciliación, pero no se duplican como hechos principales: las agregaciones se calculan desde el detalle.

