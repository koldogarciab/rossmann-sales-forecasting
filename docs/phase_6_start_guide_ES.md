# Guía en español — Fase 6: forecast final y submission de Kaggle

## Objetivo

Aplicar al test el modelo robusto seleccionado en la Fase 5:

`Recent 365-day Store + weekday + Promo`

El modelo utiliza únicamente ventas anteriores al 1 de agosto de 2015.

## Archivos nuevos

Copia:

- `06_final_forecast_submission.ipynb` en `notebooks/`
- `final_forecast.py` en `src/`
- `phase_6_start_guide_ES.md` en `docs/`

No hace falta modificar `requirements.txt`.

## Qué hace el notebook

1. Carga train, test, store y sample_submission.
2. Reconstruye las variables de las fases anteriores.
3. Calcula las medias históricas de los últimos 365 días.
4. Predice ventas para cada fila del test.
5. Asigna cero a las tiendas cerradas.
6. Trata como abiertas las 11 observaciones sin Open de Store 622.
7. Alinea las predicciones con sample_submission mediante Id.
8. Ejecuta controles de calidad.
9. Genera tablas de negocio y gráficos.
10. Guarda el CSV que se puede subir a Kaggle.

## Archivo de submission

El archivo se guardará en:

`reports/submissions/rossmann_submission_recent365.csv`

Debe contener exactamente:

- 41.088 filas;
- las columnas `Id` y `Sales`;
- los mismos Id y en el mismo orden que sample_submission;
- ningún valor nulo;
- ninguna predicción negativa.

## Otros archivos

También se generarán:

- forecast detallado por tienda y fecha;
- resumen diario;
- resumen por día de la semana;
- resumen promocional;
- resumen por tienda;
- controles finales;
- metadata del modelo;
- dos gráficos.

## Qué ejecutar

Abre:

`notebooks/06_final_forecast_submission.ipynb`

con:

`Python (rossmann-forecasting)`

Ejecuta todas las celdas en orden hasta `Stop and review`.

No hagas commit ni subas el archivo a Kaggle hasta revisar los controles.

## Qué compartir

Envía:

- resumen de las tablas de train y test;
- resumen del horizonte;
- tabla de controles;
- las 11 filas con Open imputado;
- resumen del forecast;
- primeros y últimos días;
- resumen por weekday y Promo;
- comparación de distribución;
- ambos gráficos;
- primeras y últimas filas de submission;
- archivos guardados;
- cualquier error o warning.
