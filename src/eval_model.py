import argparse
import json
import pathlib

from graph import StarGraph

from openai import OpenAI


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


def print_instance(data_path: str, client=OpenAI, shuffle: bool = False):
    dataset_path = pathlib.Path(data_path)
    with open(dataset_path, 'r') as data_file:
        graphs_dicts: list[dict] = json.load(data_file)

    pairs = list()
    for graph_dict in graphs_dicts[:1]:
        print('grafo')
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
            print("Perguntando sobre a relação", rel)

            expected_response = entity

            content = "Following is set of temporal facts. What is the entity with the"
            content += f" latest relation {rel}? Answer just with the entity name."
            content += f" Facts:\n{text_to_show}"

            chat_completion = client.chat.completions.create(messages=[
                {
                    "role": "user",
                    "content": content,
                },
            ],
                                                             model="")
            for choice in chat_completion.choices:
                response = choice.message.content
            print(response)

            pairs.append((expected_response, response))
        break
    print(pairs)


if __name__ == "__main__":
    args = config_argparser().parse_args()
    url = "http://localhost:8000/v1"
    client = OpenAI(
        api_key="foo",
        base_url=url,
    )
    print_instance(args.data, client, args.shuffle)
