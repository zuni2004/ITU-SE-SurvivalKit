import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC

# ==========================================================
# PART A — DATASET
# ==========================================================


def generate_dataset(n=100, seed=42):
    np.random.seed(seed)
    X = np.random.randn(n, 2)
    X[50:] += 5
    y = np.array([-1] * 50 + [1] * 50)
    return X, y


# ==========================================================
# PART B — TRAIN MAXIMUM MARGIN CLASSIFIER
# ==========================================================


def train_linear_svm(X, y):
    model = SVC(kernel="linear", C=1e10)
    model.fit(X, y)
    return model


# ==========================================================
# PART C — EXTRACT PARAMETERS
# ==========================================================


def extract_parameters(model):
    w = model.coef_[0]
    b = model.intercept_[0]
    return w, b


# ==========================================================
# PART D — CONSTRAINT VERIFICATION
# ==========================================================


def compute_margins(X, y, w, b):
    return y * (np.dot(X, w) + b)


def verify_constraints(margins):
    min_margin = np.min(margins)
    print(f"Minimum functional margin: {min_margin:.4f}")
    print(
        f"All constraints satisfied (margin >= 1): {min_margin >= 0.999}"
    )  # Tolerance for float precision


# ==========================================================
# PART E — GEOMETRIC MARGIN WIDTH
# ==========================================================


def compute_margin_width(w):
    return 2 / np.linalg.norm(w)


# ==========================================================
# PART F — SUPPORT VECTORS
# ==========================================================


def analyze_support_vectors(model, X, y, w, b):
    sv_indices = model.support_
    print(f"Support Vector Indices: {sv_indices}")
    print(f"Number of Support Vectors: {len(sv_indices)}")
    sv_points = X[sv_indices]
    sv_labels = y[sv_indices]
    sv_margins = sv_labels * (np.dot(sv_points, w) + b)
    print(f"Support Vector functional margins (should be approx 1):\n{sv_margins}")


# ==========================================================
# PART G — REMOVE ONE SUPPORT VECTOR
# ==========================================================


def remove_one_support_vector(model, X, y):
    idx_to_remove = model.support_[0]
    X_new = np.delete(X, idx_to_remove, axis=0)
    y_new = np.delete(y, idx_to_remove)
    return X_new, y_new


# ==========================================================
# PART H — SCALING EXPERIMENT
# ==========================================================


def scale_dataset(X, factor):
    return X * factor


# For plotting of graph
def plot_model(X, y, model, title="Model"):
    plt.figure(figsize=(8, 6))
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap="bwr", alpha=0.7)

    w = model.coef_[0]
    b = model.intercept_[0]

    x_vals = np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 100)
    y_vals = -(w[0] * x_vals + b) / w[1]
    plt.plot(x_vals, y_vals, "k-", label="Decision Boundary")

    y_margin1 = -(w[0] * x_vals + b - 1) / w[1]
    y_margin2 = -(w[0] * x_vals + b + 1) / w[1]
    plt.plot(x_vals, y_margin1, "k--", alpha=0.6, label="Margin Boundary")
    plt.plot(x_vals, y_margin2, "k--", alpha=0.6)

    plt.scatter(
        model.support_vectors_[:, 0],
        model.support_vectors_[:, 1],
        s=150,
        facecolors="none",
        edgecolors="black",
        linewidths=1.5,
        label="Support Vectors",
    )

    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.show()


if __name__ == "__main__":
    X, y = generate_dataset()
    model = train_linear_svm(X, y)
    w, b = extract_parameters(model)
    print(f"||w||: {np.linalg.norm(w):.4f}")
    margins = compute_margins(X, y, w, b)
    verify_constraints(margins)
    margin_width = compute_margin_width(w)
    print("Geometric margin width:", margin_width)
    analyze_support_vectors(model, X, y, w, b)
    plot_model(X, y, model, title="Original Maximum Margin")
    X_new, y_new = remove_one_support_vector(model, X, y)
    model_new = train_linear_svm(X_new, y_new)
    plot_model(X_new, y_new, model_new, title="After Removing Support Vector")
    X_scaled = scale_dataset(X, factor=10)
    model_scaled = train_linear_svm(X_scaled, y)
    w_scaled, _ = extract_parameters(model_scaled)
    print(f"New Margin Width after scaling: {compute_margin_width(w_scaled)}")
    plot_model(X_scaled, y, model_scaled, title="After Scaling (x10)")
