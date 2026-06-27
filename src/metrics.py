from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def _as_float_array(values: object) -> np.ndarray:
    """Convert array-like values to a one-dimensional float array."""
    array = np.asarray(values, dtype=float)

    if array.ndim != 1:
        array = np.ravel(array)

    return array


def rmspe(
    y_true: object,
    y_pred: object,
) -> float:
    """
    Calculate Root Mean Squared Percentage Error.

    Rows with an actual value of zero are excluded because percentage
    errors are undefined for those observations.
    """
    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    if actual.shape != predicted.shape:
        raise ValueError("y_true and y_pred must have the same shape.")

    valid_mask = (
        np.isfinite(actual)
        & np.isfinite(predicted)
        & (actual != 0)
    )

    if not valid_mask.any():
        raise ValueError(
            "RMSPE cannot be calculated because no non-zero actual values exist."
        )

    percentage_error = (
        actual[valid_mask] - predicted[valid_mask]
    ) / actual[valid_mask]

    return float(
        np.sqrt(
            np.mean(
                np.square(percentage_error)
            )
        )
    )


def wape(
    y_true: object,
    y_pred: object,
) -> float:
    """Calculate Weighted Absolute Percentage Error."""
    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    denominator = np.abs(actual).sum()

    if denominator == 0:
        raise ValueError(
            "WAPE cannot be calculated because the actual-value sum is zero."
        )

    return float(
        np.abs(actual - predicted).sum()
        / denominator
    )


def bias_percentage(
    y_true: object,
    y_pred: object,
) -> float:
    """Calculate aggregate forecast bias as a percentage of actual sales."""
    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    denominator = actual.sum()

    if denominator == 0:
        raise ValueError(
            "Bias percentage cannot be calculated because actual sales sum to zero."
        )

    return float(
        (predicted - actual).sum()
        / denominator
        * 100
    )


def evaluate_regression(
    y_true: object,
    y_pred: object,
    *,
    model_name: str,
    fit_seconds: float | None = None,
) -> pd.DataFrame:
    """Return a one-row table containing the main forecasting metrics."""
    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    if actual.shape != predicted.shape:
        raise ValueError("y_true and y_pred must have the same shape.")

    row = {
        "model": model_name,
        "rmspe": rmspe(actual, predicted),
        "mae": mean_absolute_error(actual, predicted),
        "rmse": mean_squared_error(
            actual,
            predicted,
        ) ** 0.5,
        "wape": wape(actual, predicted),
        "bias_pct": bias_percentage(actual, predicted),
        "evaluation_rows": len(actual),
        "positive_actual_rows": int((actual > 0).sum()),
        "fit_seconds": fit_seconds,
    }

    return pd.DataFrame([row])
