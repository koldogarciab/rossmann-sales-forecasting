# Checklist de construcción — Fase 8

## Preparación

- [ ] Ejecutar `python -m src.build_sql_model`.
- [ ] Confirmar que existen los seis CSV en `powerbi/data/`.
- [ ] Crear `powerbi/rossmann_sales_forecasting_dashboard.pbix`.
- [ ] Importar el tema `powerbi/themes/rossmann_forecast_theme.json`.

## Power Query

- [ ] Importar cada CSV por separado.
- [ ] Usar la primera fila como encabezados.
- [ ] Revisar tipos de datos.
- [ ] Aplicar y cerrar Power Query.

## Modelo

- [ ] Crear las cuatro relaciones del esquema estrella.
- [ ] Usar cardinalidad 1:* y dirección única.
- [ ] Marcar `dim_date` como tabla de fechas usando `Date`.
- [ ] Ordenar MonthName por Month.
- [ ] Ordenar DayName por DayOfWeek.
- [ ] Ocultar claves técnicas en la vista de informe.
- [ ] Crear la tabla `_Measures`.

## DAX

- [ ] Crear todas las medidas del archivo `phase_8_measures.dax`.
- [ ] Aplicar formatos numéricos correctos.
- [ ] Reconciliar los valores con `phase_8_validation_targets_ES.md`.

## Reporte

- [ ] Página 1: Executive Forecast.
- [ ] Página 2: Store Performance.
- [ ] Página 3: Promotion & Calendar.
- [ ] Página 4: Model & Data Quality.
- [ ] Revisar títulos, filtros, tooltips e interacciones.
- [ ] Verificar que ningún gráfico use columnas numéricas agregadas accidentalmente en lugar de medidas.

## Cierre

- [ ] Guardar el PBIX.
- [ ] Cerrar Power BI y comprobar GitHub Desktop.
- [ ] Revisar tamaño del PBIX.
- [ ] No hacer commit hasta la revisión final.
