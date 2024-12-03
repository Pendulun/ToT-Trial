import argparse
import json
import pathlib

from graph import StarGraph


def config_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--entities",
        type=int,
        default=10,
        required=False,
        help="Number of entities to try to add to the graph. Default 10")

    parser.add_argument("--relations",
                        type=int,
                        default=4,
                        required=False,
                        help="Number of diferent relations that could exist in the graph. "\
                        "This is not the number of edges. Default: 4")

    parser.add_argument("--shuffle",
                        action='store_true',
                        default=False,
                        help="If should shuffle the sentences at the end")

    parser.add_argument("--start-year",
                        type=int,
                        default=2000,
                        required=False,
                        help="Starting year of relations")

    parser.add_argument("--end-year",
                        type=int,
                        default=2025,
                        required=False,
                        help="End year of relations")

    parser.add_argument("--n_graphs",
                        type=int,
                        default=1,
                        required=False,
                        help="Number of graphs to generate")

    parser.add_argument("--save_to",
                        type=str,
                        default=None,
                        required=False,
                        help="Path of file to save all generated graphs")

    return parser


if __name__ == "__main__":
    args = config_argparse().parse_args()

    assert args.start_year <= args.end_year, "Starting year can't be greater than ending year!"

    entities = [f'e{i}' for i in range(1, args.entities)]
    relations = [f'r{i}' for i in range(args.relations)]
    if args.save_to is not None:
        graphs_list = list()

    for _ in range(args.n_graphs):
        graph = StarGraph()
        graph.generate_star_graph(entities, relations, args.start_year,
                                  args.end_year)
        graphs_list.append(graph.to_dict())
    if args.save_to is not None:
        file_path = pathlib.Path(args.save_to)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'a') as fp:
            json.dump(graphs_list, fp)
