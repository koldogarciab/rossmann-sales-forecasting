# Checklist final del repositorio - Fase 9

## Narrativa

- [ ] `README.md` describe el proyecto completo en inglés.
- [ ] `README_ES.md` describe el proyecto completo en castellano.
- [ ] El problema de negocio está claramente definido.
- [ ] Se justifican validación, métricas y selección del modelo.
- [ ] Se explica la decisión de no usar `Customers`.
- [ ] Se documenta la explicabilidad del modelo.
- [ ] Se traducen los resultados a indicadores empresariales.
- [ ] Se explican limitaciones y mejoras futuras.
- [ ] Se describe conceptualmente la producción.

## Reproducibilidad

- [ ] El entorno se puede crear con `environment.yml`.
- [ ] `requirements.txt` es coherente.
- [ ] Los notebooks aparecen en orden.
- [ ] Los módulos de `src/` son importables.
- [ ] El modelo SQL se construye con `python -m src.build_sql_model`.
- [ ] El notebook 09 se ejecuta sin errores.
- [ ] Las rutas del README existen.

## Resultados

- [ ] Forecast total: 247.034.117,42.
- [ ] 41.088 filas.
- [ ] 856 tiendas.
- [ ] 48 fechas.
- [ ] 35.104 días abiertos.
- [ ] 5.984 días cerrados.
- [ ] 16.252 días promocionales abiertos.
- [ ] RMSPE medio: 0,1445.
- [ ] Kaggle privado: 0,14556.
- [ ] 24/24 controles aprobados.

## Power BI

- [ ] El `.pbix` está en `powerbi/`.
- [ ] Las cuatro capturas aparecen en el README.
- [ ] Los slicers están en estado inicial.
- [ ] El informe abre sin errores.
- [ ] Las tablas y medidas reconcilian con la Fase 6.

## Higiene del repositorio

- [ ] No hay `.ipynb_checkpoints`.
- [ ] No hay `__pycache__` ni `.pyc`.
- [ ] No hay `.virtual_documents`.
- [ ] No hay bases de Anaconda accidentales.
- [ ] Los CSV raw no están trackeados.
- [ ] Los CSV exportados para Power BI no están trackeados.
- [ ] No hay archivos temporales.
- [ ] El estado final de Git está limpio.
