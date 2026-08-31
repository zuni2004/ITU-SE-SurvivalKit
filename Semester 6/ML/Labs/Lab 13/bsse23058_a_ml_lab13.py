"""
Lab 13: Drift Detection in Streaming Data
==========================================
Department of Computer and Software Engineering
SE: Machine Learning

Instructions
------------
- Complete EVERY function marked with # TODO.
- Do NOT rename any function or change its parameters or return types.
- Do NOT remove or reorder the import statements.
- You may add private helper functions anywhere below the imports.
- Run   pytest test_student.py -v   to check your work before submission.

Dataset
-------
File   : transactions_with_drift.xlsx
Sheets :
    All_Transactions       full 6-month dataset  (use for batch splitting)
    Baseline_M1_M3             months 1-3 only        (use as reference)
    Drift_Summary_Ground_Truth per-month true stats   (check AFTER all tasks)

Required packages
-----------------
    pip install pandas numpy scipy scikit-learn openpyxl matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------
# Constants — do not change these
# ------------------------------------------------------------------
DATASET_PATH = "transactions_with_drift.xlsx"
FEATURES = [
    "transaction_amount",
    "customer_age",
    "transaction_hour",
    "device_risk_score",
]
TARGET = "is_fraud"


# ==================================================================
# PART A — STREAMING DATA SIMULATION
# ==================================================================


def task1_baseline_stats(baseline_df):
    """
    Task 1: Compute summary statistics for the baseline dataset.

    Parameters
    ----------
    baseline_df : pd.DataFrame
        The Baseline_M1_M3 sheet loaded as a DataFrame.

    Returns
    -------
    stats : dict
        One key per feature in FEATURES, each mapping to a dict with:
            'mean', 'std', 'min', 'max'  (all floats)
        Plus one extra top-level key:
            'fraud_rate' : float   proportion of rows where is_fraud == 1

        Example structure:
        {
            'transaction_amount': {'mean': 2500.0, 'std': 800.0,
                                   'min': 105.3,   'max': 9870.1},
            'customer_age':       { ... },
            'transaction_hour':   { ... },
            'device_risk_score':  { ... },
            'fraud_rate': 0.03
        }
    """
    stats = {}
    for feature in FEATURES:
        stats[feature] = {
            "mean": float(baseline_df[feature].mean()),
            "std": float(baseline_df[feature].std()),
            "min": float(baseline_df[feature].min()),
            "max": float(baseline_df[feature].max()),
        }
    stats["fraud_rate"] = float((baseline_df[TARGET] == 1).mean())
    return stats


def task2_split_batches(all_df):
    """
    Task 2: Split the full dataset into six monthly batches.

    Parameters
    ----------
    all_df : pd.DataFrame
        The All_Transactions sheet loaded as a DataFrame.

    Returns
    -------
    batches : dict
        Keys   : integer month numbers 1 through 6.
        Values : pd.DataFrame containing only the rows for that month.

    Side effect
    -----------
    Save a figure 'task2_batch_means.png' with two subplots:
        - Top    : mean of transaction_amount per month (line plot)
        - Bottom : mean of transaction_hour per month   (line plot)
    """
    batches = {}
    months = sorted(all_df["month"].unique())
    for m in months:
        batches[int(m)] = all_df[all_df["month"] == m].copy()

    months_list = sorted(list(batches.keys()))
    mean_amounts = [batches[m]["transaction_amount"].mean() for m in months_list]
    mean_hours = [batches[m]["transaction_hour"].mean() for m in months_list]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    ax1.plot(months_list, mean_amounts, marker="o", color="blue")
    ax1.set_title("Mean of transaction_amount per Month")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Mean Amount")

    ax2.plot(months_list, mean_hours, marker="o", color="orange")
    ax2.set_title("Mean of transaction_hour per Month")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Mean Hour")

    plt.tight_layout()
    plt.savefig("task2_batch_means.png")
    plt.close()

    return batches


# ==================================================================
# PART B — THRESHOLD-BASED DRIFT DETECTION
# ==================================================================


def task3_mean_shift_detection(batches, baseline_stats):
    """
    Task 3: Flag monthly batches using the 2-sigma mean-shift rule.

    For each monthly batch raise a drift alert on transaction_amount if:
        | mean(batch) - mu_baseline | > 2 * sigma_baseline

    Parameters
    ----------
    batches        : dict  — output of task2_split_batches
    baseline_stats : dict  — output of task1_baseline_stats

    Returns
    -------
    alerts : dict
        Keys   : month numbers 1-6.
        Values : bool — True if drift alert triggered, False otherwise.

        Example: {1: False, 2: False, 3: False, 4: False, 5: True, 6: True}
    """
    alerts = {}
    mu_baseline = baseline_stats["transaction_amount"]["mean"]
    sigma_baseline = baseline_stats["transaction_amount"]["std"]

    for m, batch_df in batches.items():
        mu_batch = batch_df["transaction_amount"].mean()
        alerts[m] = bool(abs(mu_batch - mu_baseline) > 2 * sigma_baseline)
    return alerts


def task4_drift_log(batches, baseline_stats, alerts):
    """
    Task 4: Build a structured log of drift events.

    Only include months where alerts[month] is True.

    Parameters
    ----------
    batches        : dict  — output of task2_split_batches
    baseline_stats : dict  — output of task1_baseline_stats
    alerts         : dict  — output of task3_mean_shift_detection

    Returns
    -------
    log : list of dict
        One entry per alerted month. Each dict must have exactly:
            'month'           : int
            'drift_phase'     : str    e.g. 'Feature Drift'
            'batch_mean'      : float  mean of transaction_amount
            'shift_magnitude' : float  | batch_mean - baseline_mean |
            'sigmas_away'     : float  shift_magnitude / baseline_std

    Side effect
    -----------
    Print the log as a readable table using print().
    """
    log = []
    mu_baseline = baseline_stats["transaction_amount"]["mean"]
    sigma_baseline = baseline_stats["transaction_amount"]["std"]

    for m in sorted(batches.keys()):
        if alerts[m]:
            batch_df = batches[m]
            batch_mean = float(batch_df["transaction_amount"].mean())
            shift_magnitude = float(abs(batch_mean - mu_baseline))
            sigmas_away = (
                float(shift_magnitude / sigma_baseline) if sigma_baseline != 0 else 0.0
            )

            if (
                "drift_phase" in batch_df.columns
                and not batch_df["drift_phase"].isna().all()
            ):
                drift_phase = str(batch_df["drift_phase"].iloc[0])
            else:
                if m in [1, 2, 3]:
                    drift_phase = "Baseline"
                elif m in [4, 5]:
                    drift_phase = "Feature Drift"
                else:
                    drift_phase = "Concept Drift"

            log.append(
                {
                    "month": int(m),
                    "drift_phase": drift_phase,
                    "batch_mean": batch_mean,
                    "shift_magnitude": shift_magnitude,
                    "sigmas_away": sigmas_away,
                }
            )

    # Print table
    print(
        f"\n{'Month':<6} | {'Drift Phase':<15} | {'Batch Mean':<12} | {'Shift Mag':<10} | {'Sigmas Away':<12}"
    )
    print("-" * 60)
    for entry in log:
        print(
            f"{entry['month']:<6} | {entry['drift_phase']:<15} | {entry['batch_mean']:<12.4f} | {entry['shift_magnitude']:<10.4f} | {entry['sigmas_away']:<12.4f}"
        )

    return log


# ==================================================================
# PART C — KS TEST
# ==================================================================


def task5_ks_test(batches, baseline_df):
    """
    Task 5: Apply the KS test to detect distribution shifts.

    Compare the transaction_amount distribution of the baseline
    (Baseline_M1_M3) against each of the 6 monthly batches using
    scipy.stats.ks_2samp.

    Parameters
    ----------
    batches     : dict          — output of task2_split_batches
    baseline_df : pd.DataFrame  — the Baseline_M1_M3 DataFrame

    Returns
    -------
    ks_results : dict
        Keys   : month numbers 1-6.
        Values : dict with keys:
            'ks_stat' : float
            'p_value' : float
            'drifted' : bool   True if p_value < 0.05

        Example:
        {
            1: {'ks_stat': 0.018, 'p_value': 0.923, 'drifted': False},
            5: {'ks_stat': 0.412, 'p_value': 0.000, 'drifted': True},
        }
    """
    ks_results = {}
    baseline_vals = baseline_df["transaction_amount"].values
    for m, batch_df in batches.items():
        batch_vals = batch_df["transaction_amount"].values
        res = ks_2samp(baseline_vals, batch_vals)
        ks_results[m] = {
            "ks_stat": float(res.statistic),
            "p_value": float(res.pvalue),
            "drifted": bool(res.pvalue < 0.05),
        }
    return ks_results


def task6_method_comparison(alerts, ks_results):
    """
    Task 6: Side-by-side comparison of the two detection methods.

    Parameters
    ----------
    alerts     : dict — output of task3_mean_shift_detection
    ks_results : dict — output of task5_ks_test

    Returns
    -------
    comparison : list of dict
        One entry per month (1-6). Each dict must have exactly:
            'month'            : int
            'mean_shift_alert' : bool
            'ks_alert'         : bool
            'ks_stat'          : float
            'p_value'          : float

    Side effect
    -----------
    Print the comparison as a readable table using print().
    """
    comparison = []
    for m in sorted(alerts.keys()):
        comparison.append(
            {
                "month": int(m),
                "mean_shift_alert": bool(alerts[m]),
                "ks_alert": bool(ks_results[m]["drifted"]),
                "ks_stat": float(ks_results[m]["ks_stat"]),
                "p_value": float(ks_results[m]["p_value"]),
            }
        )

    print(
        f"\n{'Month':<6} | {'Mean Shift Alert':<16} | {'KS Alert':<8} | {'KS Stat':<8} | {'P-Value':<8}"
    )
    print("-" * 60)
    for entry in comparison:
        print(
            f"{entry['month']:<6} | {str(entry['mean_shift_alert']):<16} | {str(entry['ks_alert']):<8} | {entry['ks_stat']:<8.4f} | {entry['p_value']:<8.4e}"
        )

    return comparison


# ==================================================================
# PART D — CONCEPT DRIFT
# ==================================================================


def task7_train_baseline_model(baseline_df):
    """
    Task 7: Train a Logistic Regression classifier on the baseline data.

    Steps:
        1. Select FEATURES as inputs and TARGET as the label.
        2. Split baseline_df into 80 % train / 20 % test (random_state=42).
        3. Scale features with StandardScaler fitted on the train split only.
        4. Train LogisticRegression(max_iter=1000, random_state=42).
        5. Evaluate on the 20 % test split.

    Parameters
    ----------
    baseline_df : pd.DataFrame — the Baseline_M1_M3 DataFrame

    Returns
    -------
    model    : fitted LogisticRegression
    scaler   : fitted StandardScaler  (needed to transform future batches)
    accuracy : float   on the 20 % baseline test split
    f1       : float   binary F1-score on the 20 % baseline test split
    """
    X = baseline_df[FEATURES]
    y = baseline_df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    accuracy = float(accuracy_score(y_test, preds))
    f1 = float(f1_score(y_test, preds, average="binary"))

    return model, scaler, accuracy, f1


def task8_evaluate_on_batches(model, scaler, batches):
    """
    Task 8: Evaluate the baseline model on each monthly batch.

    Do NOT retrain the model or refit the scaler.
    Apply the same scaler from task7 to each batch before predicting.

    Parameters
    ----------
    model   : fitted LogisticRegression — first output of task7
    scaler  : fitted StandardScaler     — second output of task7
    batches : dict                      — output of task2_split_batches

    Returns
    -------
    performance : dict
        Keys   : month numbers 1-6.
        Values : dict with keys:
            'accuracy' : float
            'f1'       : float
    """
    performance = {}
    for m, batch_df in batches.items():
        X_batch = batch_df[FEATURES]
        y_batch = batch_df[TARGET]
        X_batch_scaled = scaler.transform(X_batch)
        preds = model.predict(X_batch_scaled)

        performance[m] = {
            "accuracy": float(accuracy_score(y_batch, preds)),
            "f1": float(f1_score(y_batch, preds, average="binary")),
        }
    return performance


# ==================================================================
# PART E — VISUALIZATION
# ==================================================================


def task9_drift_dashboard(batches, baseline_stats, alerts, ks_results, performance):
    """
    Task 9: Produce a 4-subplot drift dashboard and save it.

    Subplots (top to bottom):
        1. Mean of transaction_amount per month
               Draw horizontal dashed lines at mu ± 2*sigma (alert bounds)
        2. KS statistic per month
               Annotate which months are drifted (p < 0.05)
        3. Fraud rate per month  (mean of is_fraud)
        4. Model F1-score per month (from task8)

    Background shading:
        Months 4-5 : light yellow  (Feature Drift)
        Month   6   : light red     (Concept Drift)

    Parameters
    ----------
    batches        : dict — output of task2_split_batches
    baseline_stats : dict — output of task1_baseline_stats
    alerts         : dict — output of task3_mean_shift_detection
    ks_results     : dict — output of task5_ks_test
    performance    : dict — output of task8_evaluate_on_batches

    Returns
    -------
    None.  Save the figure as 'task9_drift_dashboard.png'.
    """
    months_list = sorted(list(batches.keys()))
    mean_amounts = [batches[m]["transaction_amount"].mean() for m in months_list]
    mu_baseline = baseline_stats["transaction_amount"]["mean"]
    sigma_baseline = baseline_stats["transaction_amount"]["std"]
    ks_stats = [ks_results[m]["ks_stat"] for m in months_list]
    fraud_rates = [batches[m][TARGET].mean() for m in months_list]
    f1_scores = [performance[m]["f1"] for m in months_list]

    fig, axes = plt.subplots(4, 1, figsize=(10, 14), sharex=True)

    def add_shading(ax):
        ax.axvspan(
            3.5,
            5.5,
            color="lightyellow",
            alpha=0.5,
            label="Feature Drift" if ax == axes[0] else "",
        )
        ax.axvspan(
            5.5,
            6.5,
            color="mistyrose",
            alpha=0.5,
            label="Concept Drift" if ax == axes[0] else "",
        )

    # Subplot 1: Mean Transaction Amount
    axes[0].plot(
        months_list, mean_amounts, marker="o", color="blue", label="Batch Mean"
    )
    axes[0].axhline(mu_baseline, color="black", linestyle="-", label="Baseline Mean")
    axes[0].axhline(
        mu_baseline + 2 * sigma_baseline,
        color="red",
        linestyle="--",
        label="+2 Sigma Threshold",
    )
    axes[0].axhline(
        mu_baseline - 2 * sigma_baseline,
        color="red",
        linestyle="--",
        label="-2 Sigma Threshold",
    )
    axes[0].set_ylabel("Mean trans_amount")
    axes[0].set_title("Drift Dashboard Across Months")
    axes[0].legend(loc="upper left")
    add_shading(axes[0])

    # Subplot 2: KS Statistic
    axes[1].plot(months_list, ks_stats, marker="o", color="purple")
    axes[1].set_ylabel("KS Statistic")
    for m in months_list:
        if ks_results[m]["drifted"]:
            axes[1].annotate(
                "Drifted",
                (m, ks_results[m]["ks_stat"]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
                color="red",
            )
    add_shading(axes[1])

    # Subplot 3: Fraud Rate
    axes[2].plot(months_list, fraud_rates, marker="o", color="orange")
    axes[2].set_ylabel("Fraud Rate")
    add_shading(axes[2])

    # Subplot 4: Model F1-score
    axes[3].plot(months_list, f1_scores, marker="o", color="green")
    axes[3].set_ylabel("Model F1-score")
    axes[3].set_xlabel("Month")
    add_shading(axes[3])

    plt.tight_layout()
    plt.savefig("task9_drift_dashboard.png")
    plt.close()


# ==================================================================
# MAIN — end-to-end pipeline (runs when you execute this file)
# ==================================================================

if __name__ == "__main__":
    # Load sheets
    baseline_df = pd.read_excel(DATASET_PATH, sheet_name="Baseline_M1_M3")
    all_df = pd.read_excel(DATASET_PATH, sheet_name="All_Transactions")

    # Part A
    stats = task1_baseline_stats(baseline_df)
    batches = task2_split_batches(all_df)

    # Part B
    alerts = task3_mean_shift_detection(batches, stats)
    log = task4_drift_log(batches, stats, alerts)

    # Part C
    ks_results = task5_ks_test(batches, baseline_df)
    comparison = task6_method_comparison(alerts, ks_results)

    # Part D
    model, scaler, acc, f1 = task7_train_baseline_model(baseline_df)
    performance = task8_evaluate_on_batches(model, scaler, batches)

    # Part E
    task9_drift_dashboard(batches, stats, alerts, ks_results, performance)

    print("\n--- Pipeline complete ---")
    print(f"Baseline model   Accuracy: {acc:.4f}   F1: {f1:.4f}")
    print(f"Mean-shift alerts : {[m for m, v in alerts.items() if v]}")
    print(f"KS-test alerts    : {[m for m, v in ks_results.items() if v['drifted']]}")
