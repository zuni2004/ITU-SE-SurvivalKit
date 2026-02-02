import numpy as np
import matplotlib.pyplot as plt

# Define the range for x
x = np.linspace(0, 1.5, 400)

# Define the functions
y1 = x  # Blue line
y2 = 2 * x  # Green line
y3 = 1 / x  # Red curve (xy=1 => y=1/x)

# Handle division by zero for y3 by setting the first element to infinity or a large number
with np.errstate(divide="ignore"):
    y3 = 1 / x

# Setup the plot
plt.figure(figsize=(8, 6))
plt.plot(x, y1, "b-", label="y=x")
plt.plot(x, y2, "g-", label="y=2x")
plt.plot(x, y3, "r-", label="xy=1")

# Set vertical limit to match your image
plt.ylim(0, 2)
plt.xlim(0, 1.5)

# Fill the region
# The region is bounded by y=2x on top, y=x on bottom.
# It is cut off by xy=1 on the right.
# We fill where y2 >= y1 AND y <= y3 (roughly speaking, min(y2, y3))
y_upper = np.minimum(y2, y3)  # Take the lower of the top two curves
plt.fill_between(x, y1, y_upper, where=(x <= 1), color="lightgrey", alpha=0.5)

# Labels and grid
plt.title("Region R for Q1")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.legend()
plt.show()
