import datetime

from unittest import main, TestCase

from graph import DateInterval


class TestDateInterval(TestCase):

    def test_if_intervals_overlap_start(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = DateInterval(datetime.datetime(2018, 8, 17),
                            datetime.datetime(2018, 8, 25))

        self.assertTrue(di_1.overlap(di_2))

    def test_if_intervals_overlap_end(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = DateInterval(datetime.datetime(2018, 8, 12),
                            datetime.datetime(2018, 8, 27))

        self.assertTrue(di_1.overlap(di_2))

    def test_if_intervals_overlap_equal(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))

        self.assertTrue(di_1.overlap(di_2))

    def test_if_intervals_overlap_contains(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = DateInterval(datetime.datetime(2018, 8, 16),
                            datetime.datetime(2018, 8, 20))

        self.assertTrue(di_1.overlap(di_2))

    def test_if_intervals_overlap_contained(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 22))

        self.assertTrue(di_1.overlap(di_2))

    def test_cant_compare_if_not_same_instance(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = datetime.datetime(2018, 8, 14)
        with self.assertRaises(Exception):
            di_1.overlap(di_2)

    def test_if_intervals_dont_overlap(self):
        di_1 = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        di_2 = DateInterval(datetime.datetime(2018, 8, 22),
                            datetime.datetime(2018, 8, 30))

        self.assertFalse(di_1.overlap(di_2))

    def test_to_dict(self):
        date = DateInterval(datetime.datetime(2018, 8, 15),
                            datetime.datetime(2018, 8, 20))
        strformat = "%d-%m-%Y"
        date_dict = date.to_dict(strformat)

        expected_dict = {"start_date": "15-08-2018", "end_date": "20-08-2018"}
        self.assertDictEqual(date_dict, expected_dict)


if __name__ == "__main__":
    main()
