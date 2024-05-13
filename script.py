import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

patterns = {
    "Dynamic Programming": 0,
    "Depth-First Search": 0,
    "Breadth-First Search": 0,
    "Two Pointers": 0,
    "Trie": 0,
    "Tree": 0,
    "Simulation": 0,
    "Design": 0,
    "Greedy": 0,
    "Graph": 0,
    "Bit Manipulation": 0,
    "Math": 0,
    "Matrix": 0,
    "Heap": 0,
    "Stack": 0,
    "Backtracking": 0,
    "Binary Search": 0,
    "Sliding Window": 0,
    "Basic Programming": 0,
    "Hash Function": 0,
    "Linked List": 0,
    "Database": 0,
    "Union Find": 0,
    "Adv. Data Structure": 0,
    "Recursion": 0,
    "Divide and Conquer": 0,
}

difficulty = {
    "Easy": 0,
    "Medium": 0,
    "Hard": 0,
}
company = "Facebook"

# Adjust this path to your actual Excel file location
excelfile = f"./excel sheets/{company}_questions.xlsx"
df = pd.read_excel(excelfile)

idlist = []

for index, row in df.iterrows():
    patterns_string = str(row.iloc[2])
    difficulty_string = row.iloc[4]
    problem_id = row.iloc[0]

    idlist.append(problem_id)

    # Increment the difficulty counts
    difficulty[difficulty_string] += 1

    # Increment pattern counts based on pattern string content
    for key in patterns.keys():
        if key == "Adv. Data Structure":
            if "Binary Indexed Tree" in patterns_string or "Segment Tree" in patterns_string:
                patterns[key] += 1
        elif key in patterns_string:
            patterns[key] += 1

print(idlist)

# Filtering to ensure we have the right data for visualization
graph_patterns = {k: v for k, v in patterns.items() if v > 0}
labels = list(graph_patterns.keys())
sizes = list(graph_patterns.values())

# Prepare the pie chart settings
colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
explode = [0.05] * len(labels)  # slight separation for each slice

# Create the pie chart
fig, ax = plt.subplots(figsize=(13, 12))  # Increase the figure size here
wedges, texts, autotexts = ax.pie(sizes, explode=explode, autopct='%1.1f%%', startangle=140, colors=colors)

# Adding a circle at the center to turn the pie into a donut
centre_circle = plt.Circle((0, 0), 0.70, color='black', fc='white', linewidth=0)
fig.gca().add_artist(centre_circle)

# Custom label and line drawing function
def label_line(x, y, text):
    angle = np.rad2deg(np.arctan2(y, x))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = f"angle,angleA=0,angleB={angle}"
    ax.annotate(text, xy=(x, y), xytext=(1.2*np.sign(x), 1.2*y),
                horizontalalignment=horizontalalignment,
                arrowprops=dict(arrowstyle="-", connectionstyle=connectionstyle),
                )

# Apply custom labeling function

prev_y = -99

for i, p in enumerate(wedges):
    ang = np.deg2rad((p.theta2 - p.theta1) / 2 + p.theta1)
    x = np.cos(ang)
    y = np.sin(ang)
    # adjust starting height if it's too crowded with the previous label
    if abs(y - prev_y) <= 0.05:
        if y < prev_y:
            y = prev_y - 0.06
        else:
            y = prev_y + 0.06
    prev_y = y
    label_line(x , y, labels[i])

# Set aspect ratio to be equal
ax.axis('equal')

# Title and show
chartname = f"{company} Interview Pattern Distribution"
filename = f"./charts/{company}_pattern_chart.png"

plt.title(chartname, weight="bold", fontsize=18, pad=50)
plt.savefig(filename)