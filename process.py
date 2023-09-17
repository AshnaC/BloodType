import json
import os
from pathlib import Path
import sys

from utils import construct_tree
from network import build_network

# Specify the directory path containing the JSON files

solutions_path = 'solutions'

# Initialize an empty dictionary to store the data
data_dictionary = {}


def read_problems(problem_path):
    # Iterate over the files in the directory
    for filename in os.listdir(problem_path):
        if filename.endswith('.json'):
            # Construct the file path
            file_path = os.path.join(problem_path, filename)

            # Read the JSON file
            with open(file_path, 'r') as file:
                json_data = json.load(file)

            # Convert the JSON data to a dictionary
            data_dictionary[filename] = dict(json_data)


def process_data(problem_path):
    read_problems(problem_path)
    for key in data_dictionary.keys():
        print(key)
        data = data_dictionary[key]
        tree = construct_tree(data)
        distributions = build_network(tree, data)
        solution_file_name = key.replace('problem', 'solution')
        # Specify the file path
        sol_file_path = solutions_path + '/' + solution_file_name

        # Write the dictionary as JSON to the file
        with open(sol_file_path, "w") as json_file:
            json.dump(distributions, json_file, indent=" " * 2)


def do_sample(sample):
    tree = construct_tree(sample)
    distribution = build_network(tree, sample)
    print(distribution)


# example = {
#     "family-tree": [
#
#         {
#             "relation": "father-of",
#             "subject": "Ayansh",
#             "object": "Noel"
#         },
#
#     ],
#     "test-results": [
#         {
#             "type": "cheap-bloodtype-test",
#             "person": "Omar",
#             "result": "A"
#         },
#         {
#             "type": "bloodtype-test",
#             "person": "Omar",
#             "result": "A"
#         }
#     ],
#     "queries": [
#         {
#             "type": "bloodtype",
#             "person": "Daniel"
#         },
#         {
#             "type": "bloodtype",
#             "person": "Lindsay"
#         },
#         {
#             "type": "bloodtype",
#             "person": "Samantha"
#         }
#     ]
# }
# do_sample(example)

# process_data()

if __name__ == '__main__':
    directory_path = Path(sys.argv[1]) if len(sys.argv) == 2 else 'problems'
    process_data(directory_path)
