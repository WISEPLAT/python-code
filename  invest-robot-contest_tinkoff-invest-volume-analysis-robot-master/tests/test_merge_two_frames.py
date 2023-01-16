import unittest

import pandas as pd
from pandas.util.testing import assert_frame_equal

from utils.strategy_util import merge_two_frames


class TestMergeTwoFrames(unittest.TestCase):
    def setUp(self):
        source = [
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 67.06, "quantity": 15,
             "time": "2022-05-06 06:59:44.000144+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 67.06, "quantity": 1,
             "time": "2022-05-06 06:59:44.000144+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 67.06, "quantity": 4,
             "time": "2022-05-06 06:59:44.000144+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 67.07, "quantity": 18,
             "time": "2022-05-06 07:00:00.084909+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 67.075, "quantity": 15,
             "time": "2022-05-06 07:00:00.084909+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.9, "quantity": 2,
             "time": "2022-05-06 07:00:01.119835+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.81, "quantity": 15,
             "time": "2022-05-06 07:00:05.408809+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.81, "quantity": 3,
             "time": "2022-05-06 07:00:15.605217+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.745, "quantity": 10,
             "time": "2022-05-06 07:00:46.862681+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:00:55.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:01.531078+00:00"},

            # условно потерял данные с 07:01:01 по 07:02:08

            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.795, "quantity": 50,
             "time": "2022-05-06 07:02:08.652788+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.79, "quantity": 5,
             "time": "2022-05-06 07:02:09.338233+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.88, "quantity": 25,
             "time": "2022-05-06 07:02:30.858362+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.88, "quantity": 1,
             "time": "2022-05-06 07:02:31.232032+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.9525, "quantity": 1,
             "time": "2022-05-06 07:02:58.749556+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.9, "quantity": 1,
             "time": "2022-05-06 07:03:01.484374+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.895, "quantity": 30,
             "time": "2022-05-06 07:03:55.090231+00:00"}
        ]
        self.source_df = pd.DataFrame(source, columns=["figi", "direction", "price", "quantity", "time"])

        # запрос данных с 07:01:01 по 07:02:08
        # api вернет с 07:01:00 по 07:02:59
        response = [
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:01.531078+00:00"},
            # region новые данные
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:05.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:20.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:45.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:59.531078+00:00"},
            # endregion новые данные
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.795, "quantity": 50,
             "time": "2022-05-06 07:02:08.652788+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.79, "quantity": 5,
             "time": "2022-05-06 07:02:09.338233+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.88, "quantity": 25,
             "time": "2022-05-06 07:02:30.858362+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.88, "quantity": 1,
             "time": "2022-05-06 07:02:31.232032+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.9525, "quantity": 1,
             "time": "2022-05-06 07:02:58.749556+00:00"},
        ]
        self.response_df = pd.DataFrame(response, columns=["figi", "direction", "price", "quantity", "time"])

        self.empty_df = pd.DataFrame([], columns=["figi", "direction", "price", "quantity", "time"])

    def test_merge_two_frames(self):
        expected = [
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 67.06, "quantity": 15,
             "time": "2022-05-06 06:59:44.000144+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 67.06, "quantity": 1,
             "time": "2022-05-06 06:59:44.000144+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 67.06, "quantity": 4,
             "time": "2022-05-06 06:59:44.000144+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 67.07, "quantity": 18,
             "time": "2022-05-06 07:00:00.084909+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 67.075, "quantity": 15,
             "time": "2022-05-06 07:00:00.084909+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.9, "quantity": 2,
             "time": "2022-05-06 07:00:01.119835+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.81, "quantity": 15,
             "time": "2022-05-06 07:00:05.408809+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.81, "quantity": 3,
             "time": "2022-05-06 07:00:15.605217+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.745, "quantity": 10,
             "time": "2022-05-06 07:00:46.862681+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:00:55.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:01.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:05.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:20.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:45.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.6775, "quantity": 7,
             "time": "2022-05-06 07:01:59.531078+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.795, "quantity": 50,
             "time": "2022-05-06 07:02:08.652788+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.79, "quantity": 5,
             "time": "2022-05-06 07:02:09.338233+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.88, "quantity": 25,
             "time": "2022-05-06 07:02:30.858362+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.88, "quantity": 1,
             "time": "2022-05-06 07:02:31.232032+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 1, "price": 66.9525, "quantity": 1,
             "time": "2022-05-06 07:02:58.749556+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.9, "quantity": 1,
             "time": "2022-05-06 07:03:01.484374+00:00"},
            {"figi": "BBG0013HGFT4", "direction": 2, "price": 66.895, "quantity": 30,
             "time": "2022-05-06 07:03:55.090231+00:00"}
        ]
        expected_df = pd.DataFrame(expected, columns=["figi", "direction", "price", "quantity", "time"])
        assert_frame_equal(merge_two_frames(self.source_df, self.response_df), expected_df)

    def test_boundary(self):
        assert_frame_equal(merge_two_frames(self.source_df, self.empty_df), self.source_df)
        assert_frame_equal(merge_two_frames(self.empty_df, self.response_df), self.response_df)
        assert_frame_equal(merge_two_frames(self.empty_df, self.empty_df), self.empty_df)


if __name__ == "__main__":
    unittest.main()
