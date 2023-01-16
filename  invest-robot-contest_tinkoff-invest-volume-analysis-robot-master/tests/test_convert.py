import unittest
from tinkoff.invest import Quotation

from utils.format_util import quotation_to_float


class TestConvert(unittest.TestCase):
    def test_convert_quotation_to_float(self):
        self.assertEqual(quotation_to_float(Quotation(114, 250000000)), 114.25)
        self.assertEqual(quotation_to_float(Quotation(-200, -200000000)), -200.20)
        self.assertEqual(quotation_to_float(Quotation(-0, -10000000)), -0.01)
        self.assertEqual(quotation_to_float(Quotation(0, 37180000)), 0.037180)


if __name__ == "__main__":
    unittest.main()