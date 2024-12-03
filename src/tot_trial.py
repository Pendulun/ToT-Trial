import argparse
import random

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

    return parser


if __name__ == "__main__":
    args = config_argparse().parse_args()

    assert args.start_year <= args.end_year, "Starting year can't be greater than ending year!"

    entities = [f'e{i}' for i in range(1, args.entities)]
    relations = [f'r{i}' for i in range(args.relations)]
    graph = StarGraph()
    graph.generate_star_graph(entities, relations, args.start_year,
                              args.end_year)
    if args.shuffle:
        relations = str(graph).split('\n')
        random.shuffle(relations)
        for rel in relations:
            print(rel)
    else:
        print(graph)
