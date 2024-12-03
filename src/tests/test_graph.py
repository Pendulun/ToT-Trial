from datetime import datetime
from unittest import main, TestCase
from graph import StarGraph, Relation, DateInterval


class TestStarGraph(TestCase):

    def get_graph_with_3_relations(self) -> StarGraph:
        relations_to_add = [
            Relation('e1',
                     DateInterval(datetime(2000, 5, 6), datetime(2001, 5, 6))),
            Relation('e2',
                     DateInterval(datetime(2001, 6, 6), datetime(2002, 5, 6))),
            Relation('e3',
                     DateInterval(datetime(2002, 6, 6), datetime(2003, 5, 6)))
        ]

        graph = StarGraph()
        for relation in relations_to_add:
            graph.add_edge('r1', relation)
        return graph

    def test_to_list(self):
        graph = self.get_graph_with_3_relations()
        self.assertEqual(3, len(graph.to_list()))

    def test_empty_to_list(self):
        graph = StarGraph()
        self.assertEqual(0, len(graph.to_list()))

    def test_shuffled_list(self):
        graph = self.get_graph_with_3_relations()
        self.assertEqual(3, len(graph.shuffled_list()))

    def test_str(self):
        graph = self.get_graph_with_3_relations()
        graph_str = str(graph)
        self.assertEqual(3, len(graph_str.split("\n")))

    def test_len(self):
        graph = self.get_graph_with_3_relations()
        self.assertEqual(3, len(graph))

    def test_empty_len(self):
        graph = StarGraph()
        self.assertEqual(0, len(graph))


if __name__ == "__main__":
    main()
