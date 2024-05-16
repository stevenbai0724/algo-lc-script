import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import yaml as yaml
import openai
from dotenv import dotenv_values
import os
from openai import OpenAI

data = {
    "pattern": {
        "pattern_chart": "",
        "difficulty_chart": "",
        "summary": (
        ),
    }
}
data["pattern"]["summary"] = "The Snowflake technical interview process leans heavily on data structures and algorithms, with a particular emphasis on dynamic programming, breadth-first and depth-first searches. The problems tend to be moderately challenging, with a fair mixture of intermediate to more advanced problems. Many of these problems would fall into the Leetcode medium to hard categories. It's also worth noting that many of the problems seem to involve graphs and trees, which suggests that applicants need to be comfortable with solving real-world problems involving these structures.\n\nIn preparing for the technical interview, it's crucial to understand and recognize common coding patterns such as backtracking, binary search, design patterns, graph theory, and basic math problems. Remember, the majority of these problems are not 'trick' problems - they're meant to assess your problem-solving skills, your understanding of algorithms and data structures, and your ability to write clean, efficient code. Therefore, practicing is essential. Leetcode has a large set of problems you can use for practice, and recognizing patterns in these problems will greatly benefit you in the technical interview."
def str_presenter(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def sequence_presenter(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(str, str_presenter, Dumper=yaml.SafeDumper)
yaml.add_representer(list, sequence_presenter, Dumper=yaml.SafeDumper)

# Write the data to a YAML file
with open(f"testing.yaml", "w") as file:
    yaml.dump(data, file, default_flow_style=False, sort_keys=False, Dumper=yaml.SafeDumper, width=4096)

