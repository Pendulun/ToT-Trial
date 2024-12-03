import random
import datetime
import calendar


class DateInterval():
    """
    A Date Interval with some utility functions
    """

    strformat = "%d-%m-%Y"

    def __init__(self, start_date: datetime.datetime,
                 end_date: datetime.datetime):
        assert_msg = f"Start date ({start_date}) must be before end date ({end_date})! "
        assert start_date <= end_date, assert_msg
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

    @classmethod
    def get_random(cls, years: list = None, seed: int = None):
        """
        Returns a random DateInterval in the years interval provided
        """
        random.seed(seed)
        months = list(range(1, 13))
        if years is None:
            years = list(range(2000, 2025))

        starting_date, finishing_date = cls._get_start_and_end_date(
            cls._get_random_date(years, months),
            cls._get_random_date(years, months))

        return DateInterval(starting_date, finishing_date)

    @classmethod
    def _get_random_date(cls, years: list[int], months: list[int]):
        random_year = random.choice(years)
        random_month = random.choice(months)
        _, final_day = calendar.monthrange(random_year, random_month)
        random_day = random.choice(list(range(1, final_day)))

        return datetime.datetime(random_year, random_month, random_day)

    @classmethod
    def _get_start_and_end_date(cls, first_date, second_date):
        if first_date < second_date:
            return first_date, second_date

        if first_date > second_date:
            return second_date, first_date

        return first_date, second_date

    def to_dict(self, strformat: str = None) -> dict:
        """
        Returns a dict following: {'start_date':'...', 'end_date':'...'}
        """
        if strformat is None:
            strformat = self.strformat

        self_dict = dict()
        self_dict['start_date'] = self.start.strftime(strformat)
        self_dict['end_date'] = self.end.strftime(strformat)
        return self_dict

    @classmethod
    def from_dict(cls, target_dict: dict, strformat: str = None):
        """
        Create a DataInterval object from a dict.
        The dict must follow: {'start_date':'...', 'end_date':"..."} 
        """
        if strformat is None:
            strformat = cls.strformat
        start_date = datetime.datetime.strptime(target_dict['start_date'],
                                                strformat)
        end_date = datetime.datetime.strptime(target_dict['end_date'],
                                              strformat)
        return DateInterval(start_date, end_date)

    def _assert_same_instance(self, other):
        assert isinstance(
            other,
            DateInterval), f"Cant compare {type(other)} with DateInterval!"

    def __eq__(self, other):
        self._assert_same_instance(other)
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))

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
        """
        Returns if this Relation overlaps it DateInterval wiith another
        """
        return self.date_interval.overlap(other.date_interval)

    def to_dict(self) -> dict:
        """
        Returns a dict of this Relation following: 
        {'name':'...', 'date_interval':{...}}.
        See DateInterval.to_dict() for more
        """
        self_dict = dict()
        self_dict['name'] = self.name
        self_dict["date_interval"] = self.date_interval.to_dict()
        return self_dict

    @staticmethod
    def from_dict(target_dict: dict) -> 'Relation':
        """
        Returns a Relation object from the target dict
        """
        name = target_dict['name']
        date_interval = DateInterval.from_dict(target_dict['date_interval'])
        return Relation(name, date_interval)

    def __gt__(self, other: 'Relation'):
        return self.date_interval > other.date_interval

    def __le__(self, other: 'Relation'):
        return self.date_interval <= other.date_interval

    def __eq__(self, other: 'Relation'):
        if self.name != other.name:
            return False

        if self.date_interval != other.date_interval:
            return False

        return True

    def __hash__(self):
        return hash((self.name, self.date_interval))

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

    def new_random_valid_relation_with(
            self,
            entity,
            years: list[int],
            n_tries: int = 5,
            seed: int | list[int] = None) -> Relation:
        """
        Try to create a new random relation using the entity
        with a DateInterval in the years passed. It will try
        to add a relation for n_tries times. It may fail if
        it dont generate valid DateIntervals for the relation.
        A valid DateInterval is one that dont overlap with
        anyother relation.
        The first try is done with the seed provided. All the
        others are made with random seed.
        """
        seeds = list()
        if seed is None:
            seeds = [None] * n_tries
        elif type(seed) == list:
            if len(seed) < n_tries:
                seed.extend([None] * (n_tries - len(seed)))
        elif type(seed) == int:
            seeds = [seed]
            seed.extend([None] * (n_tries - 1))
        else:
            raise TypeError(
                f"seed should be one of (int, list[int], None) but {type(seed)} was provided!"
            )

        for id_try in range(n_tries):
            random.seed(seeds[id_try])
            new_relation = Relation(entity,
                                    DateInterval.get_random(years, seed))

            if self._dont_overlap_with_any_relation(new_relation):
                self._relations.add(new_relation)
                return new_relation

        return None

    def _dont_overlap_with_any_relation(self, new_relation):
        for relation in self._relations:
            if relation.overlap(new_relation):
                return False

        return True

    def add(self, relation: Relation) -> bool:
        """
        Tries to add the new relation to this collection.
        It wont be added if it overlaps with any 
        existing relation.
        Returns if the relation was added or not
        """
        if self._dont_overlap_with_any_relation(relation):
            self._relations.add(relation)
            return True

        return False

    def latest(self) -> Relation:
        """
        Get the latest relation from this collection
        """
        latest_rel = None
        for relation in self._relations:
            if latest_rel is None or relation > latest_rel:
                latest_rel = relation

        return latest_rel

    def to_dict(self) -> dict:
        """
        Returns a dict of this Relations following:
        {'rel_name':'...',
        'relations':[{...}, {...}]}
        See Relation.to_dict() for more.
        """
        self_dict = dict()
        self_dict['rel_name'] = self._relation_name

        self_dict['relations'] = [
            relation.to_dict()
            for relation in sorted(self._relations, reverse=True)
        ]
        return self_dict

    @staticmethod
    def from_dict(target_dict: dict) -> 'Relations':
        rel_name = target_dict['rel_name']
        relations_obj = Relations(rel_name)
        for rel_dict in target_dict['relations']:
            relations_obj.add(Relation.from_dict(rel_dict))

        return relations_obj

    def has(self, relation: Relation) -> bool:
        """
        Check if this Relations has a relation.
        """
        for rel in self._relations:
            if rel == relation:
                return True
        return False

    def __str__(self):
        final_str = ""
        for relation in self._relations:
            final_str += f"Relation {self._relation_name} with {relation}, "

        return final_str.strip(",")

    def __eq__(self, other):
        if self._relation_name != other._relation_name:
            return False

        if len(self._relations) != len(other._relations):
            return False

        for rel in self._relations:
            if not other.has(rel):
                return False

        return True

    def __iter__(self):
        yield from self._relations


class StarGraph():
    """
    As this is a Star Graph, all relations have one end with the central node (e0).
    """

    def __init__(self):
        self.relations_map: dict[str, Relations] = dict()

    def generate_star_graph(self,
                            entities: list[int],
                            relations: list[int],
                            start_year: int = 2000,
                            end_year: int = 2025):
        entities_copy = entities.copy()
        random.shuffle(entities_copy)

        years = list(range(start_year, end_year))

        self.relations_map = dict()
        for entity in entities_copy:
            relation = random.choice(relations)
            curr_relations: Relations = self.relations_map.setdefault(
                relation, Relations(relation))
            curr_relations.new_random_valid_relation_with(entity, years)

    def add_edge(self, relation_name: str, relation: Relation):
        """
        Add an edge with the central node
        """
        self.relations_map.setdefault(relation_name,
                                      Relations(relation_name)).add(relation)

    def to_list(self) -> list[str]:
        """
        Returns a list of strings of Relations inside this graph
        """
        if len(self.relations_map) == 0:
            return list()

        final_str = ""
        for key in sorted(self.relations_map.keys()):
            final_str += str(self.relations_map[key])

        final_str = final_str.strip(", ")
        return [relation.strip() for relation in final_str.split(",")]

    def shuffled_list(self, seed: int = None) -> list[str]:
        """
        Returns a shuffled list of strings of Relations inside this graph
        """
        random.seed(None)
        graph_list = self.to_list()
        random.shuffle(graph_list)
        return graph_list

    def get_all_latest(self) -> dict[str, str]:
        latest_relations = dict()
        for rel_name, relations in self.relations_map.items():
            latest = relations.latest().name
            latest_relations[rel_name] = latest

        return latest_relations

    def to_dict(self) -> dict:
        """
        Returns a dict of this Graph following:
        {rel_name:[
            'name':'...', 
            'relations':{...}, {...}
            ]
        }
        See Relations.to_dict() for more.
        """
        self_dict = dict()
        self_dict = {
            rel: relations.to_dict()
            for rel, relations in self.relations_map.items()
        }
        return self_dict

    @classmethod
    def from_dict(cls, target_dict: dict[str, dict]) -> 'StarGraph':
        """
        Returns a StarGraph object from the target_dict.
        """
        graph = StarGraph()
        for rel_name, relations_dict in target_dict.items():
            for relation_dict in relations_dict['relations']:
                graph.add_edge(rel_name, Relation.from_dict(relation_dict))

        return graph

    def has(self, rel_name: str, target_relation: Relation) -> bool:
        """
        Check if this graph has a target_relation of type rel_name
        """
        if rel_name not in self.relations_map:
            return False

        return self.relations_map[rel_name].has(target_relation)

    def n_relation_types(self) -> int:
        """
        Return the number of diferent relations types this graph has. This is
        not the number of edges, but their labels
        """
        return len(list(self.relations_map.keys()))

    def mean_nodes_per_relation_type(self) -> float:
        """
        Return the number of nodes divided by the number of relations
        """
        return len(self) / self.n_relation_types()

    def __len__(self):
        return len(self.to_list())

    def __str__(self):
        self_list = [el + "\n" for el in self.to_list()]
        self_list[-1] = self_list[-1].strip("\n")
        return "".join(self_list)

    def __eq__(self, other: 'StarGraph'):
        if len(self) != len(other):
            return False

        for rel_name, relations in self.relations_map.items():
            for relation in relations:
                if not other.has(rel_name, relation):
                    return False

        return True
