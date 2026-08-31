"""
Lab 7 Starter Code
Agglomerative Clustering from Scratch
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

# ============================================================
# DATASET
# ============================================================


def generate_dataset():

    X, _ = make_blobs(n_samples=100, centers=3, cluster_std=1.2, random_state=42)

    return X


# ============================================================
# PART A
# ============================================================


def compute_distance_matrix(X):

    n = len(X)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            # Euclidean distance formula [cite: 54]
            dist = np.sqrt(np.sum((X[i] - X[j]) ** 2))
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix


# ============================================================
# PART B
# ============================================================


def linkage_distance(cluster1, cluster2, X, method="single"):

    distances = []
    for idx1 in cluster1:
        for idx2 in cluster2:
            dist = np.sqrt(np.sum((X[idx1] - X[idx2]) ** 2))
            distances.append(dist)

    if method == "single":
        return np.min(distances)
    elif method == "complete":
        return np.max(distances)
    elif method == "average":
        return np.mean(distances)
    return 0


# ============================================================
# PART C
# ============================================================


def find_closest_clusters(clusters, X, method):

    min_dist = float("inf")
    closest_pair = (None, None)

    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            dist = linkage_distance(clusters[i], clusters[j], X, method)
            if dist < min_dist:
                min_dist = dist
                closest_pair = (i, j)

    return closest_pair[0], closest_pair[1], min_dist


# ============================================================
# MODEL
# ============================================================


class MyAgglomerative:

    def __init__(self, n_clusters=3, linkage="single"):

        self.n_clusters = n_clusters
        self.linkage = linkage

        self.labels_ = None
        self.history_ = []

    def fit(self, X):

        n = len(X)

        clusters = [[i] for i in range(n)]
        current_cluster_ids = list(range(n))
        next_cluster_id = n

        while len(clusters) > self.n_clusters:

            i, j, dist = find_closest_clusters(clusters, X, self.linkage)
            self.history_.append(
                [
                    current_cluster_ids[i],
                    current_cluster_ids[j],
                    dist,
                    len(clusters[i]) + len(clusters[j]),
                ]
            )

            new_cluster = clusters[i] + clusters[j]

            idx_to_remove = sorted([i, j], reverse=True)
            for idx in idx_to_remove:
                clusters.pop(idx)
                current_cluster_ids.pop(idx)

            clusters.append(new_cluster)
            current_cluster_ids.append(next_cluster_id)
            next_cluster_id += 1

        self.labels_ = np.zeros(n)
        for label, cluster in enumerate(clusters):
            for point_idx in cluster:
                self.labels_[point_idx] = label

    def predict(self, X):
        return self.labels_


# ============================================================
# VISUALIZATION
# ============================================================


def plot_clusters(X, labels, title):

    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap="viridis")
    plt.title(title)


# ============================================================
# DENDROGRAM (BONUS)
# ============================================================


def plot_dendrogram(history):

    linkage_matrix = np.array(history).astype(float)
    plt.figure(figsize=(10, 7))
    dendrogram(linkage_matrix)
    plt.title("Agglomerative Clustering Dendrogram")
    plt.xlabel("Sample Index")
    plt.ylabel("Distance")
    plt.show()


# ============================================================
# MAIN
# ============================================================


def main():

    X = generate_dataset()

    model = MyAgglomerative(n_clusters=3, linkage="single")

    model.fit(X)

    labels = model.predict(X)
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plot_clusters(X, labels, "Custom Agglomerative (Single)")
    plot_dendrogram(model.history_)

    plt.show()


if __name__ == "__main__":
    main()
