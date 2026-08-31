"""
Lab 4 Starter Code
Hard vs Soft Margin using C, Hinge Loss and Kernels

INSTRUCTIONS
------------
You will NOT implement SVM training.
You will use sklearn.

Your tasks are:

PART A:
Observe effect of C on clean and overlapping datasets.

PART B:
Observe noise sensitivity using large vs small C.

PART C:
Implement hinge loss and compute violations.

PART D:
Use kernels to separate nonlinear data.

DO NOT MODIFY:
- dataset functions
- evaluation helpers
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC

# ============================================================
# DATASETS (DETERMINISTIC)
# ============================================================


def dataset_clean():
    """
    D1: Clean Separable Dataset

    Description:
    - 10 points in 2D
    - First 5 points are positive class (+1)
    - Last 5 points are negative class (-1)
    - Fully linearly separable without overlap

    Instructions for students:
    - Use this dataset to observe SVM behaviour when data is clean
    - Suitable for Part A (effect of C)
    - Can visualize points using scatter plot with colors
    """
    X = np.array(
        [[3, 3], [4, 3], [3, 4], [5, 4], [4, 5], [1, 1], [2, 1], [1, 2], [2, 2], [2, 3]]
    )
    y = np.array([1, 1, 1, 1, 1, -1, -1, -1, -1, -1])
    return X, y


def dataset_overlap():
    """
    D2: Overlapping Dataset

    Description:
    - 12 points in 2D
    - First 5 points are positive class (+1)
    - Two points in between classes to create overlap
    - Last 5 points are negative class (-1)
    - Not fully separable; some points lie in margin

    Instructions for students:
    - Use this dataset to see how SVM handles overlap
    - Observe how decision boundary changes with different C values
    - Useful for Part A (effect of C) and Part C (hinge loss analysis)
    """
    X = np.array(
        [
            [3, 3],
            [4, 3],
            [3, 4],
            [5, 4],
            [4, 5],
            [2.5, 2.5],
            [2.7, 2.3],
            [1, 1],
            [2, 1],
            [1, 2],
            [2, 2],
            [2, 3],
        ]
    )
    y = np.array([1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1])
    return X, y


def dataset_noisy():
    """
    D3: Noisy Dataset

    Description:
    - Based on dataset_clean
    - Two points intentionally misclassified (y values flipped)
    - Simulates noise in labels

    Instructions for students:
    - Use this dataset to see how SVM handles label noise
    - Compare model behaviour for very large vs small C
    - Useful for Part B (noise sensitivity)
    """
    X, y = dataset_clean()
    y[0] = -1  # introduce misclassification
    y[3] = -1
    return X, y


# ============================================================
# MODEL TRAINING
# ============================================================


def train_svm(X, y, C=1, kernel="linear"):
    """
    Train a SVM using sklearn.

    Instructions for students:
    - Use sklearn.svm.SVC with the specified kernel and C.
    - Fit the model to the dataset (X, y).
    - Return the trained model.
    """
    model = SVC(kernel=kernel, C=C)
    model.fit(X, y)
    return model


# ============================================================
# HINGE LOSS
# ============================================================


def hinge_loss(X, y, w, b):
    """
    Compute total hinge loss for a linear model.

    Instructions for students:
    - For each sample (x_i, y_i), compute:
        loss_i = max(0, 1 - y_i * (w^T x_i + b))
    - Sum over all samples to get total hinge loss.
    - Return the total loss.
    - Do NOT include any sklearn functions here; use only numpy.
    """
    projections = np.dot(X, w) + b
    loss_array = np.maximum(0, 1 - y * projections)
    return np.sum(loss_array)


# ============================================================
# EXTRACT MODEL PARAMETERS
# ============================================================


def get_w_b(model):
    """
    Extract weight vector and bias from a trained linear SVM.

    Instructions for students:
    - model.coef_ contains w
    - model.intercept_ contains b
    - Return w and b as numpy arrays/scalars
    """
    w = model.coef_[0]
    b = model.intercept_[0]
    w = np.where(np.abs(w) < 1e-9, 1e-6, w)
    return w, b


# ============================================================
# PART A
# ============================================================


def part_A_effect_of_C():
    """
    Investigate effect of C on clean and overlapping datasets.

    Instructions for students:
    - Load dataset_clean() and dataset_overlap()
    - Train SVM with C = 0.01, 1, 1000 (use train_svm)
    - For each model:
        - Plot decision boundary and margins
        - Compare how boundaries change with C
    - Observe how large C leads to hard-margin-like behaviour
    """
    C_vals = [0.1, 1, 1.5, 2]
    datasets = [(dataset_clean(), "Clean"), (dataset_overlap(), "Overlap")]

    for data, name in datasets:
        X, y = data
        plt.figure(figsize=(16, 4))
        for i, c in enumerate(C_vals):
            plt.subplot(1, 4, i + 1)
            model = train_svm(X, y, C=c)
            plot_svc_decision_boundary(model, X, y, f"{name} (C={c})")
        plt.show()


# ============================================================
# PART B
# ============================================================


def part_B_noise_sensitivity():
    """
    Analyze noise sensitivity using D3.

    Instructions for students:
    - Load dataset_noisy()
    - Train SVM with:
        - Very large C (e.g., 1000)
        - Small C (e.g., 0.01)
    - Plot both decision boundaries on the same figure
    - Observe which one is more robust to misclassified points
    """
    X, y = dataset_noisy()
    C_vals = [0.1, 2]

    plt.figure(figsize=(10, 4))
    for i, c in enumerate(C_vals):
        plt.subplot(1, 2, i + 1)
        model = train_svm(X, y, C=c)
        plot_svc_decision_boundary(model, X, y, f"Noisy Data (C={c})")
    plt.show()


# ============================================================
# PART C
# ============================================================


def part_C_hinge_analysis():
    """
    Compute hinge loss for dataset_overlap.

    Instructions for students:
    - Load dataset_overlap()
    - Train SVM with several C values (e.g., 0.01, 1, 10, 100)
    - Extract w, b for each model using get_w_b()
    - Compute total hinge loss using hinge_loss()
    - Compare magnitude of hinge loss for different C
    - Optional: count number of support vectors (model.support_vectors_)
    - Optional: plot decision boundaries for visualization
    """
    X, y = dataset_overlap()
    C_vals = [0.1, 1, 1.5, 2]

    print("--- Part C: Hinge Loss Analysis ---")
    for c in C_vals:
        model = train_svm(X, y, C=c)
        w, b = get_w_b(model)
        total_loss = hinge_loss(X, y, w, b)
        n_sv = len(model.support_vectors_)
        print(f"C={c:3} | Total Hinge Loss: {total_loss:.4f} | Support Vectors: {n_sv}")


# ============================================================
# PART D
# ============================================================


def generate_circles():
    from sklearn.datasets import make_circles

    X, y = make_circles(n_samples=200, noise=0.05, factor=0.5, random_state=0)
    y[y == 0] = -1
    return X, y


def part_D_kernels():
    """
    Use kernel SVMs to separate nonlinear data.

    Instructions for students:
    - Generate concentric circles dataset using generate_circles()
    - Train SVM using:
        - linear kernel
        - polynomial kernel
        - rbf kernel
    - Plot decision boundaries for each kernel
    - Compare performance and separability
    """
    X, y = generate_circles()
    kernels = ["linear", "poly", "rbf"]

    plt.figure(figsize=(15, 5))
    for i, knl in enumerate(kernels):
        plt.subplot(1, 3, i + 1)
        # Using C=1.5 from the list
        model = train_svm(X, y, C=1.5, kernel=knl)
        plot_svc_decision_boundary(model, X, y, f"Kernel: {knl}")
    plt.show()


def plot_svc_decision_boundary(model, X, y, title):
    plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap=plt.cm.Paired)
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    xx = np.linspace(xlim[0], xlim[1], 30)
    yy = np.linspace(ylim[0], ylim[1], 30)
    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T
    Z = model.decision_function(xy).reshape(XX.shape)

    ax.contour(
        XX,
        YY,
        Z,
        colors="k",
        levels=[-1, 0, 1],
        alpha=0.5,
        linestyles=["--", "-", "--"],
    )

    ax.scatter(
        model.support_vectors_[:, 0],
        model.support_vectors_[:, 1],
        s=100,
        linewidth=1,
        facecolors="none",
        edgecolors="k",
        label="Support Vectors",
    )
    plt.title(title)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    part_A_effect_of_C()
    part_B_noise_sensitivity()
    part_C_hinge_analysis()
    part_D_kernels()
