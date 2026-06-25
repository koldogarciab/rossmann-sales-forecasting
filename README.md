# Rossmann Retail Sales Forecasting & FP&A Analytics

An end-to-end machine learning project to forecast daily store sales and translate forecast performance into FP&A and business-controlling insights.

## Current status

**Phase 0 — Project setup**  
**Phase 1 — Business understanding and data audit**

The first notebook validates the raw Kaggle files before any cleaning, feature engineering, or modelling decisions are made.

## Data

Download the Rossmann Store Sales competition files from Kaggle and place the following files in `data/raw/`:

- `train.csv`
- `store.csv`
- `test.csv`
- `sample_submission.csv`

Raw data is intentionally excluded from Git.

## Environment

Using Conda:

```bash
conda env create -f environment.yml
conda activate rossmann-forecasting
python -m ipykernel install --user --name rossmann-forecasting --display-name "Python (rossmann-forecasting)"
jupyter lab
```

Open `notebooks/01_data_audit.ipynb` and run the cells from top to bottom.

## Important modelling decision

`Customers` is available in the historical training data but not in the Kaggle test data and would normally be unavailable when preparing a future forecast. It may be used for descriptive analysis, but it will not be used as a principal production predictor.
