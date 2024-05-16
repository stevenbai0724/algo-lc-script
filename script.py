import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import yaml as yaml
import openai
from dotenv import dotenv_values
from unicodedata import normalize
import os
from openai import OpenAI

# yaml config
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def replace_placeholders(config, placeholders):
    config_str = yaml.dump(config)
    for key, value in placeholders.items():
        config_str = re.sub(r'\$\{' + key + r'\}', value, config_str)
    return yaml.safe_load(config_str)

config_path = './config.yaml'  # Update this path as needed
yaml_config = load_config(config_path)

placeholders = {'company': yaml_config['company']}

yaml_config = replace_placeholders(yaml_config, placeholders)

company = yaml_config["company"]
excelfile = yaml_config["directories"]["excel_file"]

df = pd.read_excel(excelfile)

patterns = yaml_config["patterns"]
difficulty = yaml_config["difficulty"]

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
            ax.annotate(text, xy=(x, y), xytext=(1.2*np.sign(x), 1.2*y),
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
        filename = yaml_config["directories"]["pattern_chart"]

        plt.title(chartname, weight="bold", fontsize=18, pad=50)
        plt.savefig(filename)

    def plot_difficulty(difficulty):
        colors = ['#34a853','#eb4334', '#fbbc02']

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.pie(difficulty.values(), labels=difficulty.keys(), autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        chartname = f"{company} Interview Question Difficulty"
        filename = yaml_config["directories"]["difficulty_chart"]

        plt.title(chartname, weight="bold", fontsize=18, pad=50)
        plt.savefig(filename)

    # sum up patterns and difficulty
    for index, row in df.iterrows():
        patterns_string = str(row.iloc[2])
        difficulty_string = str(row.iloc[4])
        problem_id = int(row.iloc[0])

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

    #OpenAI config
    client = OpenAI()
    config = dotenv_values(".env")
    client.api_key = config["OPENAI_API_KEY"]

    new_patterns = {k: v for k, v in patterns.items() if v > 0}
    res = ""

    data = {
        "title": f"{company} Interview Patterns",
        "questions": idlist,
        "pattern": {
            "pattern_chart": "",
            "difficulty_chart": "",
            "summary": (
                ""
            ),
        }
    }

    # prompt
    messages = [
        {"role": "system", "content": "You need to write a technical interview guide for a specific company. The position is for software engineering and the problems are leetcode-style coding challenges with patterns like dfs/bfs, two pointers, dynamic programming, etc. user provdes the pattern distribution data and you need to write 1-3 paragraphs about the trends and briefly the difficulty level, and how to prepare by identifying common patterns and listing some leetcode problems. do not output the distribution data."},
        {"role": "user", "content": f"please write a technical interview guide for {company}. here is the pattern distrbution for the interview: {str(new_patterns)}. do not mention the problem frequency counts. provide 2-3 paragraphs each separated by two newlines. provde problem list hyperlinked separated by newlines after the paragraphs. hyper links should be like this: '- [Minimum Number of Keypresses (Sorting + Greedy)](https://algo.monster/liteproblems/2268)\\n' where the link is to algo.monster/liteproblems followed by leetcode problem ID number. the returned response should just be first paragraph\\n\\nsecondparagraph\\n\\n- [list item1](https://)\\n- [list item2](https://)\\n). "}
    ]
    completion = client.chat.completions.create(
        model="gpt-4",
        max_tokens=2048,
        messages=messages
    )
    res = completion.choices[0].message.content
    res.replace(":", "")
    res.replace('\\n', '\n')
    res = re.sub(r'[ \t]+\n', '\n', res)
    
    data["pattern"]["summary"] = res

    # Custom representer to format the output into desired yaml
    def str_presenter(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    def sequence_presenter(dumper, data):
        return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

    yaml.add_representer(str, str_presenter, Dumper=yaml.SafeDumper)
    yaml.add_representer(list, sequence_presenter, Dumper=yaml.SafeDumper)

    # Write the data to a YAML file
    with open(f"{company}.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False, Dumper=yaml.SafeDumper, width=4096)

main()