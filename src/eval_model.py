import argparse
from collections.abc import Generator
from collections import namedtuple
import json
import math
import pathlib
import re

from dotenv import dotenv_values
from tqdm import tqdm

from evaluators import LLM, URLLLM, HuggingFaceQuestionAnsweringLLM
from graph import StarGraph

DataInstance = namedtuple(
    "DataInstance",
    ['graph_id', 'relation_name', 'target_entity', 'relations'])

LLM_answer_max_tokens = 20


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

    parser.add_argument("--batch_s",
                        type=int,
                        required=False,
                        default=1,
                        help="The batch size. It might not be used")

    parser.add_argument(
        "--url",
        type=str,
        required=False,
        default="http://localhost:8000/v1",
        help=
        "URL for the model. Default: http://localhost:8000/v1 as when running local-llm"
    )

    parser.add_argument(
        "--model_name",
        type=str,
        required=False,
        default="",
        help=
        "The model name to be used such as microsoft/Phi-3-mini-4k-instruct. Default is ''"
        + " as when running with local-llm")

    parser.add_argument(
        "--qa",
        action="store_true",
        default=False,
        required=False,
        help=
        "If it should use the question-answering pipeline from Hugging Face")

    parser.add_argument(
        "--chat",
        action="store_true",
        default=False,
        required=False,
        help="If it should use the chat pipeline from Hugging Face")
    return parser


def get_eval_pair(data_path: str,
                  shuffle: bool = False,
                  n_instances: int = -1,
                  batch_s: int = 1) -> Generator[list[DataInstance]]:
    """
    Generator that returns data instances to be evaluated.
    data_path: The path to the data
    shuffle: If it should shuffle the relations text
    n_instances: Number to limit total instances generated.
    batch_s: The batch size
    """
    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    instance_count = 0
    reached_n_instances = False
    batch = list()
    for graph_id, graph_dict in enumerate(graphs_dicts):
        graph = StarGraph.from_dict(graph_dict)

        text_to_show = graph.get_shuffled_str() if shuffle else str(graph)

        for rel, entity in graph.get_all_latest().items():
            if instance_count == n_instances:
                reached_n_instances = True
                break

            if len(batch) == batch_s:
                yield batch
                batch = list()

            batch.append(DataInstance(graph_id, rel, entity, text_to_show))
            instance_count += 1

        if reached_n_instances:
            break

    if len(batch) > 0:
        yield batch


def run(data_path: str,
                   llm: LLM,
                   shuffle: bool = False,
                   n_graphs: int = -1,
                   n_instances: int = -1,
                   batch_s: int = 1):
    assert type(
        batch_s
    ) == int, f"Batch size must be an integer but {type(batch_s)} was given!"
    assert batch_s > 0, f"Batch size must be positive but {batch_s} was given!"

    context_fmt = "The following is a set of temporal facts."
    context_fmt += " All dates are in the format year-month-day. Facts:\n{}"
    question_fmt = "What is the entity with the latest relation {}?"
    question_fmt += " Answer just with the entity name."

    pairs = list()

    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    total_instances = get_total_instances(n_graphs, n_instances, graphs_dicts)

    n_batches = int(math.ceil(total_instances / batch_s))

    for batch in tqdm(get_eval_pair(data_path,
                                    shuffle,
                                    n_instances=total_instances,
                                    batch_s=batch_s),
                      total=n_batches):
        batch_info = list()
        for instance in batch:
            batch_info.append({
                'context':
                context_fmt.format(instance.relations),
                'question':
                question_fmt.format(instance.relation_name)
            })

        responses = llm.answer(batch_info, max_tokens=LLM_answer_max_tokens)
        for instance, response in zip(batch, responses):
            target_info = re.findall("e[0-9]+", response['answer'])
            final_answer = ''
            if len(target_info) > 0:
                final_answer = target_info[0]
            pairs.append((instance.target_entity, final_answer))

    return pairs


def get_total_instances(n_graphs: int, n_instances: int,
                        graphs_dicts: list[dict]) -> int:
    """
    Calculate the total number of instances that will be evaluated
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
    secrets = dotenv_values(".env")
    model_type = None
    if args.qa:
        model_type = 'qa'
    elif args.chat:
        model_type = 'chat'
    else:
        model_type = 'local'

    type_to_model = {'qa': HuggingFaceQuestionAnsweringLLM, 'local': URLLLM}

    llm = type_to_model[model_type](args.model_name, args.url,
                                    secrets['API_KEY'])
    pairs = run(args.data, llm, args.shuffle, args.n_graphs,
                           args.n_instances, args.batch_s)
