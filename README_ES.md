# Rossmann Retail Sales Forecasting & FP&A Analytics

Proyecto end-to-end de Machine Learning para predecir ventas diarias por tienda y traducir el rendimiento del forecast a conclusiones útiles para FP&A y business controlling.

## Estado actual

**Fase 0 — Preparación del proyecto**  
**Fase 1 — Comprensión del negocio y auditoría de datos**

El primer notebook valida los archivos originales antes de tomar decisiones de limpieza, feature engineering o modelización.

## Datos

Descarga desde Kaggle los archivos de la competición Rossmann Store Sales y colócalos en `data/raw/`:

- `train.csv`
- `store.csv`
- `test.csv`
- `sample_submission.csv`

Los datos originales están excluidos de Git.

## Entorno

Con Anaconda Prompt abierto en la carpeta del proyecto:

```bash
conda env create -f environment.yml
conda activate rossmann-forecasting
python -m ipykernel install --user --name rossmann-forecasting --display-name "Python (rossmann-forecasting)"
jupyter lab
```

Abre `notebooks/01_data_audit.ipynb` y ejecuta las celdas en orden.

## Decisión importante

`Customers` existe en el histórico de entrenamiento, pero no en el test de Kaggle y normalmente no estaría disponible al preparar un forecast futuro. Podrá utilizarse en análisis descriptivo, pero no como predictor principal del modelo de producción.
