# Guía de inicio - Fase 9

## Objetivo

Cerrar la narrativa técnica y empresarial del proyecto mediante:

- README final en inglés y castellano;
- explicabilidad intrínseca del modelo seleccionado;
- traducción del forecast a métricas de negocio;
- arquitectura end-to-end;
- propuesta conceptual de producción, monitorización y reentrenamiento;
- capturas validadas del dashboard;
- auditoría final de la estructura del repositorio.

## Archivos del paquete

Copia el contenido del ZIP en la raíz del repositorio. Los archivos `README.md` y `README_ES.md` sustituyen las versiones iniciales, que todavía indican que el proyecto se encuentra en la Fase 1.

## Primer bloque de ejecución

1. Extrae el ZIP directamente dentro de `rossmann-sales-forecasting`.
2. Confirma que se han copiado:
   - los dos README;
   - `notebooks/09_explainability_business_impact.ipynb`;
   - los documentos de `docs/`;
   - las figuras y capturas;
   - `scripts/final_repository_audit.py`.
3. Abre el notebook 09 con el kernel `Python (rossmann-forecasting)`.
4. Ejecuta todas las celdas.
5. Revisa los resultados esperados antes de hacer commit.
6. Ejecuta desde la raíz:

```bash
python scripts/final_repository_audit.py
```

No hagas commit todavía. Primero revisaremos juntos el notebook, las figuras, los README y el resultado de la auditoría.

## Resultados esperados del notebook

- Forecast sales: 247.034.117,42
- Forecast rows: 41.088
- Forecast stores: 856
- Forecast dates: 48
- Open store days: 35.104
- Closed store days: 5.984
- Promo open store days: 16.252
- Promo uplift: aproximadamente 35,0 %
- Top 10 stores share: aproximadamente 3,16 %
- Top 50 stores share: aproximadamente 11,15 %

## Qué compartir para la revisión

- salida inicial del notebook;
- tabla de KPIs;
- tabla del efecto promocional;
- tabla de concentración;
- tres gráficos generados;
- resultado completo de `final_repository_audit.py`;
- captura de GitHub Desktop con los archivos modificados, sin commit.
