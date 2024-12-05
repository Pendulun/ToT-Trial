import argparse
from collections.abc import Generator
from collections import namedtuple
import json
import pathlib

from graph import StarGraph

from openai import OpenAI

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
    return parser


def get_eval_pair(data_path: str,
                  shuffle: bool = False,
                  n_graphs_to_eval: int = 1) -> Generator[DataInstance]:
    """
    Generator that returns a data instance to be evaluated at a time.
    data_path: The path to the data
    shuffle: If it should shuffle the relations text
    n_graphs_to_eval: Number of graphs to get instances from.
    A non positive number would yield all instances
    """
    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    for graph_id, graph_dict in enumerate(graphs_dicts):
        print("GRAPH ID:", graph_id)
        graph = StarGraph.from_dict(graph_dict)

        text_to_show = ""
        if shuffle:
            text_to_show = ""
            for text in graph.shuffled_list():
                text_to_show += text + "\n"
            text_to_show = text_to_show.strip("\n")
        else:
            text_to_show = str(graph)

        for rel, entity in graph.get_all_latest().items():
            yield DataInstance(graph_id, rel, entity, text_to_show)

        if graph_id + 1 >= n_graphs_to_eval:
            break


def print_instance(data_path: str, client=OpenAI, shuffle: bool = False):
    content_fmt = "The following is a set of temporal facts. All dates are in the format year-month-day."
    content_fmt += " What is the entity with the latest relation {}? Answer just with the entity name."
    content_fmt += " Facts:\n{}"

    pairs = list()
    for data_instance in get_eval_pair(data_path, shuffle):
        print("NEW DATA==============")
        curr_content = content_fmt.format(data_instance.relation_name,
                                          data_instance.relations)

        print(curr_content)
        chat_completion = client.chat.completions.create(messages=[
            {
                "role": "user",
                "content": curr_content,
            },
        ],
                                                         model="")
        for choice in chat_completion.choices:
            response = choice.message.content
        print(response)

        pairs.append((data_instance.target_entity, response))

    print(pairs)


if __name__ == "__main__":
    args = config_argparser().parse_args()
    url = "http://localhost:8000/v1"
    client = OpenAI(
        api_key="foo",
        base_url=url,
    )
    print_instance(args.data, client, args.shuffle)
