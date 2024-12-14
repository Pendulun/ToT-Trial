import argparse
from collections.abc import Generator
from collections import namedtuple
import json
import math
import pathlib
import re

from dotenv import dotenv_values
from tqdm import tqdm

from evaluators import LLM, URLLLM, HuggingFaceQuestionAnsweringLLM, HuggingFaceChatLLM
from graph import StarGraph
import utils

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

    parser.add_argument("--starting_batch",
                        type=int,
                        required=False,
                        default=0,
                        help="The batch id from where to start evaluating. "\
                            " Usefull to continue running after a halt. Default: 0")

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

    parser.add_argument("--results_path",
                        type=str,
                        required=True,
                        help="The path to the csv file to save the results")

    parser.add_argument("--print-times",
                        action="store_true",
                        required=False,
                        default=False,
                        help="If it should print times.")

    parser.add_argument("--no-progress",
                        action="store_true",
                        required=False,
                        default=False,
                        help="If it should not show the progress bar")

    parser.add_argument(
        "--apply_regex",
        action="store_true",
        default=False,
        help=
        "If it should apply regex to filter out the entity of the llm response."\
            " If not used, will save the original responseI"
    )
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

            batch.append(DataInstance(graph_id, rel, entity.name,
                                      text_to_show))
            instance_count += 1

        if reached_n_instances:
            break

    if len(batch) > 0:
        yield batch


def run(data_path: str,
        llm: LLM,
        results_path: str,
        shuffle: bool = False,
        n_graphs: int = -1,
        n_instances: int = -1,
        batch_s: int = 1,
        starting_batch: int = 0,
        no_progress_bar: bool = False,
        apply_regex: bool = True):
    assert type(
        batch_s
    ) == int, f"Batch size must be an integer but {type(batch_s)} was given!"
    assert batch_s > 0, f"Batch size must be positive but {batch_s} was given!"

    context_fmt = "The following is a set of temporal facts."
    context_fmt += " All dates are in the format year-month-day. Facts:\n{}"
    question_fmt = "What is the entity with the latest relation {}?"
    question_fmt += " Answer just with the entity name."

    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    results_path: pathlib.Path = pathlib.Path(results_path)
    results_path.parent.mkdir(exist_ok=True, parents=True)

    if starting_batch == 0:
        with open(results_path, 'w') as result_file:
            result_file.write("graph_id,rel_name,expected,predicted\n")

    total_instances = get_total_instances(n_graphs, n_instances, graphs_dicts)

    n_batches = int(math.ceil(total_instances / batch_s))

    for batch_id, batch in enumerate(
            tqdm(get_eval_pair(data_path,
                               shuffle,
                               n_instances=total_instances,
                               batch_s=batch_s),
                 total=n_batches,
                 desc="Batches",
                 disable=no_progress_bar)):
        if batch_id < starting_batch:
            continue

        batch_results = proccess_batch(llm,
                                       context_fmt,
                                       question_fmt,
                                       batch,
                                       apply_regex=apply_regex)
        save_results_to(batch_results, results_path)


@utils.timer_dec
def proccess_batch(
        llm: LLM,
        context_fmt: str,
        question_fmt: str,
        batch: list[DataInstance],
        apply_regex: bool = True) -> list[tuple[int, str, str, str]]:
    """
    Proccess the batch of data using the provided llm.
    Return a list of responses
    """
    batch_info = list()
    for instance in batch:
        batch_info.append({
            'context':
            context_fmt.format(instance.relations),
            'question':
            question_fmt.format(instance.relation_name)
        })

    responses = llm.answer(batch_info, max_tokens=LLM_answer_max_tokens)

    batch_results = post_process_answers(batch, responses, apply_regex)
    return batch_results


@utils.timer_dec
def save_results_to(batch_results: list[tuple[int, str, str, str]],
                    results_path: pathlib.Path):
    with open(results_path, 'a') as result_file:
        lines = [
            ",".join([str(el) for el in result]) + "\n"
            for result in batch_results
        ]
        result_file.writelines(lines)


@utils.timer_dec
def post_process_answers(
        batch: list[DataInstance],
        llm_responses: list[dict],
        apply_regex: bool = True) -> list[tuple[int, str, str, str]]:
    batch_results = list()
    for instance, response in zip(batch, llm_responses):
        final_answer = response['answer']
        if apply_regex:
            target_info = re.findall("e[0-9]+", response['answer'])
            final_answer = target_info[0] if len(target_info) > 0 else ''
        batch_results.append((instance.graph_id, instance.relation_name,
                              instance.target_entity, final_answer))
    return batch_results


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
        graph_instances = graph.n_relation_types()
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

    type_to_model = {
        'qa': HuggingFaceQuestionAnsweringLLM,
        'local': URLLLM,
        'chat': HuggingFaceChatLLM
    }

    llm = type_to_model[model_type](args.model_name, args.url,
                                    secrets['API_KEY'])

    if not args.print_times:
        utils.PRINT_ENABLED = False

    run(args.data, llm, args.results_path, args.shuffle, args.n_graphs,
        args.n_instances, args.batch_s, args.starting_batch, args.no_progress,
        args.apply_regex)
