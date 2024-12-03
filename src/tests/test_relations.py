from datetime import datetime
from unittest import main, TestCase
from graph import Relations, Relation, DateInterval


class TestRelations(TestCase):

    def test_add_one_relation(self):
        relation = Relation(
            'r1', DateInterval(datetime(2018, 6, 19), datetime(2020, 6, 19)))
        relations = Relations('r1')
        self.assertTrue(relations.add(relation))

    def test_dont_add_overlapping_relation(self):
        relations = Relations('r1')
        first_relation = Relation(
            'r1', DateInterval(datetime(2018, 6, 19), datetime(2020, 6, 19)))

        overlapping_relation = Relation(
            'r1', DateInterval(datetime(2019, 4, 2), datetime(2021, 3, 23)))

        relations.add(first_relation)
        self.assertFalse(relations.add(overlapping_relation))

    def test_get_latest_relation(self):
        relations = Relations("r1")
        relations_to_add = [
            Relation(
                'r1', DateInterval(datetime(2018, 6, 19),
                                   datetime(2020, 6, 19))),
            Relation('r1',
                     DateInterval(datetime(2013, 4, 2), datetime(2015, 3,
                                                                 23))),
            Relation('r1',
                     DateInterval(datetime(2021, 4, 2), datetime(2023, 3, 23)))
        ]
        for relation in relations_to_add:
            relations.add(relation)

        self.assertIs(relations.latest(), relations_to_add[2])
    
    def test_latest_relation_is_none(self):
        relations = Relations("r1")
        self.assertIsNone(relations.latest())

    def test_get_random_valid_relation(self):
        relations = Relations("r1")
        relations_to_add = [
            Relation(
                'e2', DateInterval(datetime(2018, 6, 19),
                                   datetime(2020, 6, 19))),
            Relation('e3',
                     DateInterval(datetime(2013, 4, 2), datetime(2015, 3, 23)))
        ]
        for relation in relations_to_add:
            relations.add(relation)

        new_relation = relations.new_random_valid_relation_with(
            'e1', [2003, 2004, 2005])
        self.assertIsNotNone(new_relation)


if __name__ == "__main__":
    main()
