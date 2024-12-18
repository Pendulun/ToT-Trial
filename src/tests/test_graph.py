from datetime import datetime
from unittest import main, TestCase
from graph import StarGraph, Relation, DateInterval


class TestStarGraph(TestCase):

    def get_graph_with_3_relations_single_type(self) -> StarGraph:
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
        graph = self.get_graph_with_3_relations_single_type()
        self.assertEqual(3, len(graph.to_list()))

    def test_empty_to_list(self):
        graph = StarGraph()
        self.assertEqual(0, len(graph.to_list()))

    def test_shuffled_list(self):
        graph = self.get_graph_with_3_relations_single_type()
        self.assertEqual(3, len(graph.shuffled_list()))

    def test_str(self):
        graph = self.get_graph_with_3_relations_single_type()
        graph_str = str(graph)
        self.assertEqual(3, len(graph_str.split("\n")))

    def test_len(self):
        graph = self.get_graph_with_3_relations_single_type()
        self.assertEqual(3, len(graph))

    def test_empty_len(self):
        graph = StarGraph()
        self.assertEqual(0, len(graph))

    def get_graph_dict(self) -> dict:
        target_dict = {
            'r1': {
                'rel_name':
                'r1',
                'relations': [{
                    'name': 'e3',
                    'date_interval': {
                        'start_date': '06-06-2002',
                        'end_date': '06-05-2003'
                    }
                }, {
                    'name': 'e2',
                    'date_interval': {
                        'start_date': '06-06-2001',
                        'end_date': '06-05-2002'
                    }
                }, {
                    'name': 'e1',
                    'date_interval': {
                        'start_date': '06-05-2000',
                        'end_date': '06-05-2001'
                    }
                }]
            }
        }

        return target_dict

    def test_to_dict(self):
        graph = self.get_graph_with_3_relations_single_type()
        expected_dict = self.get_graph_dict()

        self.assertDictEqual(expected_dict, graph.to_dict())

    def test_from_dict(self):
        target_dict = self.get_graph_dict()

        expected_graph = self.get_graph_with_3_relations_single_type()
        resuting_graph = StarGraph.from_dict(target_dict)
        self.assertEqual(expected_graph, resuting_graph)

    def _get_graph_with_relations_of_2_types(self):
        rel_to_relations = {
            'r1': [
                Relation(
                    'e1',
                    DateInterval(datetime(2000, 5, 6), datetime(2001, 5, 6))),
                Relation(
                    'e2',
                    DateInterval(datetime(2001, 6, 6), datetime(2002, 5, 6))),
                Relation(
                    'e3',
                    DateInterval(datetime(2002, 6, 6), datetime(2003, 5, 6)))
            ],
            'r2': [
                Relation(
                    'e4',
                    DateInterval(datetime(2030, 5, 6), datetime(2031, 7, 29))),
                Relation(
                    'e5',
                    DateInterval(datetime(2005, 4, 15), datetime(2009, 3, 2))),
                Relation(
                    'e6',
                    DateInterval(datetime(2022, 3, 19), datetime(2029, 4, 6)))
            ]
        }
        graph = StarGraph()
        for rel_name, rels in rel_to_relations.items():
            for rel in rels:
                graph.add_edge(rel_name, rel)
        return graph

    def test_get_latest_relations(self):
        graph = self._get_graph_with_relations_of_2_types()

        expected_latests = {
            'r1':
            Relation('e3',
                     DateInterval(datetime(2002, 6, 6), datetime(2003, 5, 6))),
            'r2':
            Relation('e4',
                     DateInterval(datetime(2030, 5, 6), datetime(2031, 7, 29)))
        }
        self.assertDictEqual(expected_latests, graph.get_all_latest())

    def test_get_all_latest_str(self):
        graph = self._get_graph_with_relations_of_2_types()

        n_relations = len(graph.get_all_latest_str().split("\n"))
        self.assertEqual(n_relations, 2)

    def test_get_shuffled_text(self):
        graph = self.get_graph_with_3_relations_single_type()
        self.assertNotEqual(graph.get_shuffled_str(42), str(graph))

    def test_get_n_relations(self):
        graph = self._get_graph_with_relations_of_2_types()
        self.assertEqual(6, graph.n_relations())

    def test_get_interleaved_list(self):
        graph = self._get_graph_with_relations_of_2_types()
        self.assertEqual(6, len(graph.get_interleaved_list()))

    def test_get_interleaved_str(self):
        graph = self._get_graph_with_relations_of_2_types()
        n_relations = len(graph.get_interleaved_str().split("\n"))
        self.assertEqual(n_relations, 6)

    def test_sorted_ascending(self):
        graph = self._get_graph_with_relations_of_2_types()
        for relations in graph.relations_map.values():
            sorted_rels = relations.sorted()
            #Check if every relation comes before the next one
            for idx, rel in enumerate(sorted_rels):
                if idx < len(sorted_rels) - 1:
                    self.assertTrue(rel <= sorted_rels[idx + 1])

    def test_sorted_descending(self):
        graph = self._get_graph_with_relations_of_2_types()
        for relations in graph.relations_map.values():
            sorted_rels = relations.sorted(ascending=False)
            #Check if every relation comes after the next one
            for idx, rel in enumerate(sorted_rels):
                if idx < len(sorted_rels) - 1:
                    self.assertTrue(rel >= sorted_rels[idx + 1])

    def test_can_get_n_relations_for_relation(self):
        graph = self._get_graph_with_relations_of_2_types()
        self.assertEqual(graph.n_nodes_for_relation('r1'), 3)

    def test_get_0_for_non_existent_relation(self):
        graph = self._get_graph_with_relations_of_2_types()
        self.assertEqual(graph.n_nodes_for_relation('j9'), 0)


if __name__ == "__main__":
    main()
