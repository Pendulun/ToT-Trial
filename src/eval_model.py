import argparse
from collections.abc import Generator
from collections import namedtuple
import json
import pathlib

from tqdm import tqdm

from evaluators import Evaluator, LocalLLMEvaluator
from graph import StarGraph

DataInstance = namedtuple(
    "DataInstance",
    ['graph_id', 'relation_name', 'target_entity', 'relations'])


def config_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data",
                        type=str,
                        required=True,
                        help="The dataset path")

    parser.add_argument("--shuffle",
                        action="store_true",
                        required=False,
                        default=False,
                        help="If the context should be shuffled")

    parser.add_argument("--n_graphs",
                        type=int,
                        required=False,
                        default=-1,
                        help="Num of graphs to evaluate. Default -1 (all)")

    parser.add_argument(
        "--n_instances",
        type=int,
        required=False,
        default=-1,
        help="Num of total instances to evaluate. Default -1 (all)")
    return parser


def get_eval_pair(data_path: str,
                  shuffle: bool = False,
                  n_instances: int = -1) -> Generator[DataInstance]:
    """
    Generator that returns a data instance to be evaluated at a time.
    data_path: The path to the data
    shuffle: If it should shuffle the relations text
    n_instances: Number to limit total instances generated.
    """
    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    instance_count = 0
    reached_n_instances = False
    for graph_id, graph_dict in enumerate(graphs_dicts):
        graph = StarGraph.from_dict(graph_dict)

        text_to_show = graph.get_shuffled_str() if shuffle else str(graph)

        for rel, entity in graph.get_all_latest().items():
            if instance_count == n_instances:
                reached_n_instances = True
                break

            yield DataInstance(graph_id, rel, entity, text_to_show)
            instance_count += 1

        if reached_n_instances:
            break


def print_instance(data_path: str,
                   evaluator: Evaluator,
                   shuffle: bool = False,
                   n_graphs: int = -1,
                   n_instances: int = -1):
    content_fmt = "The following is a set of temporal facts. All dates are in the format year-month-day."
    content_fmt += " What is the entity with the latest relation {}? Answer just with the entity name."
    content_fmt += " Facts:\n{}"

    pairs = list()

    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    total_instances = get_total_instances(n_graphs, n_instances, graphs_dicts)

    for data_instance in tqdm(get_eval_pair(data_path,
                                            shuffle,
                                            n_instances=total_instances),
                              total=total_instances):
        curr_content = content_fmt.format(data_instance.relation_name,
                                          data_instance.relations)

        # response = evaluator.answer(curr_content)
        response = ""
        pairs.append((data_instance.target_entity, response))

    print(pairs)


def get_total_instances(n_graphs: int, n_instances: int,
                        graphs_dicts: list[dict]) -> int:
    """
    Calculate to total number of instances that will be generated
    """
    tot_instances = 0
    for graph_id, graph_dict in enumerate(graphs_dicts):
        if graph_id == n_graphs:
            break

        graph = StarGraph.from_dict(graph_dict)
        graph_instances = graph.n_relations()
        if n_instances < 0:
            tot_instances += graph_instances
        elif tot_instances + graph_instances < n_instances:
            tot_instances += graph_instances
        else:
            tot_instances = n_instances
            break

    return tot_instances


if __name__ == "__main__":
    args = config_argparser().parse_args()
    url = "http://localhost:8000/v1"
    evaluator = LocalLLMEvaluator(url)
    print_instance(args.data, evaluator, args.shuffle, args.n_graphs,
                   args.n_instances)
