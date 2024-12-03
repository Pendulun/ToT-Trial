import argparse
from collections import Counter
import json
import pathlib
import pandas as pd

from graph import StarGraph


def config_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data",
                        type=str,
                        required=True,
                        help="The dataset path")

    parser.add_argument("--save_to",
                        type=str,
                        required=True,
                        help="Where to save the stats")

    return parser


def save_stats(data_path: str, save_to: str):
    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    graph_sizes = list()
    relation_count = list()
    mean_nodes_per_relation = list()
    for graph_dict in graphs_dicts:
        graph = StarGraph.from_dict(graph_dict)
        graph_sizes.append(len(graph))
        relation_count.append(graph.n_relation_types())

    df = pd.DataFrame()
    df['nodes'] = graph_sizes
    df['relations'] = relation_count
    df.to_csv(save_to, index=False)


if __name__ == "__main__":
    args = config_argparser().parse_args()

    save_stats(args.data, args.save_to)
