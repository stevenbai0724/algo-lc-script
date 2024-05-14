import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yaml as yaml
import openai
from dotenv import dotenv_values
import os
from openai import OpenAI

company = "Facebook"
excelfile = f"./excel sheets/{company}_questions.xlsx"
df = pd.read_excel(excelfile)

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

# topics that are mutually exclusive with "basic programming" pattern
not_basics = ["Dynamic Programming", "Depth-First Search", "Breadth-First Search", "Trie", "Simulation", "Graph", "Recursion"]

# list of problem ID's for liteproblem link
idlist = []

def generate_charts():
    def plot_patterns(graph_patterns):
        labels = list(graph_patterns.keys())
        sizes = list(graph_patterns.values())

        # Prepare the pie chart settings
        colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
        explode = [0.05] * len(labels)  # slight separation for each slice

        # Create the pie chart
        fig, ax = plt.subplots(figsize=(14, 12))  # Increase the figure size here
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, autopct='%1.1f%%', startangle=140, colors=colors)

        # Adding a circle at the center to turn the pie into a donut
        centre_circle = plt.Circle((0, 0), 0.70, color='black', fc='white', linewidth=0)
        fig.gca().add_artist(centre_circle)

        # Custom label and line drawing function
        def label_line(x, y, text):
            angle = np.rad2deg(np.arctan2(y, x))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={angle}"
            ax.annotate(text, xy=(x, y), xytext=(1.25*np.sign(x), 1.2*y),
                        horizontalalignment=horizontalalignment,
                        arrowprops=dict(arrowstyle="-", connectionstyle=connectionstyle),
                        )
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

    def plot_difficulty(difficulty):
        colors = ['#34a853', '#fbbc02', '#eb4334']

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.pie(difficulty.values(), labels=difficulty.keys(), autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        chartname = f"{company} Interview Question Difficulty"
        filename = f"./charts/{company}_difficulty_chart.png"

        plt.title(chartname, weight="bold", fontsize=18, pad=50)
        plt.savefig(filename)

    # sum up patterns and difficulty
    for index, row in df.iterrows():
        patterns_string = str(row.iloc[2])
        difficulty_string = str(row.iloc[4])
        problem_id = str(row.iloc[0])

        idlist.append(problem_id)

        # Increment the difficulty counts
        difficulty[difficulty_string] += 1

        # Check for each pattern in the string and increment if found
        if "Easy" in difficulty_string:
            isBasic = True
            for pattern in not_basics:
                if pattern in difficulty_string:
                    isBasic = False
            if isBasic:
                patterns["Basic Programming"] += 1

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
    difficulty_data = {k: v for k, v in difficulty.items() if v > 0}

    plot_patterns(graph_patterns)
    plot_difficulty(difficulty_data)

def main():
    generate_charts()

    #config
    client = OpenAI()
    config = dotenv_values(".env")
    client.api_key = config["OPENAI_API_KEY"]

    new_patterns = {k: v for k, v in patterns.items() if v > 0}

    # roles: system, user, assistant
    # system - sets the behavior of the assistant
    # user - provides requests or comments for the assistant to respond to
    # assistant - stores previous assistant responses
    messages = [
        {"role": "system", "content": "You need to write a technical interview guide for a specific company. The position is for software engineering and the problems are leetcode-style coding challenges with patterns like dfs/bfs, two pointers, dynamic programming, etc. user provdes the pattern distribution data and you need to write 1-3 paragraphs about the trends and difficulty level (briefly) and how to prepare by identifying common patterns and listing some leetcode problems. do not output the distribution data. output in yaml format ready to be exported. provide good examples of questions and hyperlink them in lists, pipe symbol to separate paragraphs."},
        {"role": "user", "content": f"please write a technical interview guide for {company}. here is the pattern distrbution for the interview: {str(new_patterns)}. do not mention the problem frequency counts."}
    ]

    completion = client.chat.completions.create(
        model="gpt-4",
        max_tokens=2048,
        messages=messages
    )

    print(completion.choices[0].message.content)

    file_path = 'interview_preparation_guide.yaml'
    with open(file_path, 'w') as file:
        file.write(completion.choices[0].message.content.strip())

main()

