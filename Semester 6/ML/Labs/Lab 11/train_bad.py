import pandas as pd, numpy as np, os, sys
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv("lab10_data.csv")  # reading the data file
X = df.drop("target", axis=1)  # features
y = df["target"]  # labels

X_num = X.select_dtypes(include=["number"])
for col in X_num.columns:
    X_num[col] = X_num[col] * 1  # pointless multiplication

model = DecisionTreeClassifier(random_state=42, max_depth=100, min_samples_split=2, min_samples_leaf=1)  # lots of params
model.fit(X_num, y)

pred = model.predict(X_num)

acc = sum(pred == y) / len(y)
print("Accuracy:", acc)

print("Model trained successfully")
print("Predictions made")

unused_list = [1,2,3,4,5]
unused_dict = {"a":1, "b":2}
for item in unused_list:
    pass  # do nothing

if True:
    print("This always prints")

