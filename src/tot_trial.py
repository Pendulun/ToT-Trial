import random
import datetime
import calendar


class DateInterval():
    """
    A Date Interval with some utility functions
    """

    def __init__(self, start_date: datetime.datetime,
                 end_date: datetime.datetime):
        self.start = start_date
        self.end = end_date

    def overlap(self, other) -> bool:
        """
        Return if this DateInterval overlaps with another
        """
        self._assert_same_instance(other)
        equal = self.start == other.start
        start_overlap = self.start < other.start and self.end > other.start
        end_overlap = self.start < other.end and self.end > other.end
        contains = self.start <= other.start and self.end >= other.end
        contained = self.start >= other.start and self.end <= other.end
        return equal or start_overlap or end_overlap or contains or contained

    def _assert_same_instance(self, other):
        assert isinstance(
            other,
            DateInterval), f"Cant compare {type(other)} with DateInterval!"

    def __eq__(self, other):
        self._assert_same_instance(other)
        return self.start == other.start and self.end == other.end

    def __lt__(self, other):
        self._assert_same_instance(other)
        return self.end < other.start

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __str__(self) -> str:
        return f"{self.start.date()} to {self.end.date()}"


class Relation():
    """
    This represents a Relation. It has a name and a DateInterval
    """

    def __init__(self, name, date_interval: DateInterval):
        self.name = name
        self.date_interval: DateInterval = date_interval

    def _assert_same_instance(self, other):
        isinstance(other,
                   Relation), f"Cant compare {type(other)} with Relation!"

    def overlap(self, other: "Relation"):
        return self.date_interval.overlap(other.date_interval)

    def __str__(self) -> str:
        return f"{self.name} in time interval {self.date_interval}"


class Relations():
    """
    This is a collection of Relation.
    It can create a new random relation or add another 
    to itself
    """

    def __init__(self, relation_name):
        self._relation_name = relation_name
        self._relations: set[Relation] = set()

    def __len__(self):
        return len(self._relations)

    def new_random_relation_with(self,
                                 entity,
                                 years: list[int],
                                 n_tries: int = 5):
        """
        Try to create a new random relation using the entity
        with a DateInterval in the years passed. It will try
        to add a relation for n_tries times. It may fail if
        it dont generate valid DateIntervals for the relation.
        A valid DateInterval is one that dont overlap with
        anyother relation.
        """
        months = list(range(1, 13))
        for _ in range(n_tries):
            starting_date, finishing_date = self.get_start_and_end_date(
                self.get_random_date(years, months),
                self.get_random_date(years, months))

            new_relation_date_interval = DateInterval(starting_date,
                                                      finishing_date)

            new_relation = Relation(entity, new_relation_date_interval)

            if self._dont_overlap_with_any_relation(new_relation):
                self._relations.add(new_relation)
                break

    def _dont_overlap_with_any_relation(self, new_relation):
        valid_relation_date_range = True
        for relation in self._relations:
            if relation.overlap(new_relation):
                valid_relation_date_range = False
        return valid_relation_date_range

    def add(self, relation: Relation):
        """
        Tries to add the new relation to this collection.
        It wont be added if it overlaps with any 
        existing relation
        """
        if self._dont_overlap_with_any_relation(relation):
            self._relations.add(relation)

    def latest(self) -> Relation:
        """
        Get the latest relation from this collection
        """
        latest_rel = None
        for relation in self._relations:
            if latest_rel is None or latest_rel > relation:
                latest_rel = relation

        return latest_rel

    def __str__(self):
        final_str = ""
        for relation in self._relations:
            final_str += f"Relation {self._relation_name} with {relation}, "

        return final_str.strip(",")

    def get_random_date(self, years: list[int], months: list[int]):
        random_year = random.choice(years)
        random_month = random.choice(months)
        _, final_day = calendar.monthrange(random_year, random_month)
        random_day = random.choice(list(range(1, final_day)))

        return datetime.datetime(random_year, random_month, random_day)

    def get_start_and_end_date(self, first_date, second_date):
        if first_date < second_date:
            return first_date, second_date

        if first_date > second_date:
            return second_date, first_date

        return first_date, second_date


class StarGraph():
    """
    As this is a Star Graph, all relations have one end with the central node (e0)
    """

    def __init__(self):
        self.relations_map: dict[int, Relations] = dict()

    def generate_star_graph(self, entities: list[int], relations: list[int]):
        entities_copy = entities.copy()
        random.shuffle(entities_copy)

        years = list(range(2000, 2025))

        self.relations_map = dict()
        for entity in entities_copy:
            relation = random.choice(relations)
            curr_relations: Relations = self.relations_map.setdefault(
                relation, Relations(relation))
            curr_relations.new_random_relation_with(entity, years)

    def add_relation_with(self, relation_name: str, relation: Relation):
        self.relations_map.setdefault(relation_name, Relations).add(relation)

    def __str__(self):
        final_str = ""
        for relation in self.relations_map.values():
            final_str += str(relation)

        return final_str.strip(", ")


if __name__ == "__main__":
    entities = [f'e{i}' for i in range(1, 10)]
    relations = [f'r{i}' for i in range(1, 4)]
    graph = StarGraph()
    graph.generate_star_graph(entities, relations)
    relations = [relation.strip() for relation in str(graph).split(",")]
    random.shuffle(relations)
    print(relations)
