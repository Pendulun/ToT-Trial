import random

from graph import StarGraph


if __name__ == "__main__":
    entities = [f'e{i}' for i in range(1, 10)]
    relations = [f'r{i}' for i in range(1, 4)]
    graph = StarGraph()
    graph.generate_star_graph(entities, relations)
    relations = [relation.strip() for relation in str(graph).split(",")]
    random.shuffle(relations)
    print(relations)
