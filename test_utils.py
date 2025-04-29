# test_utils.py
import unittest
from utils import calculate_wpm, calculate_accuracy  # Import the functions


class TestCalculations(unittest.TestCase):

    def test_calculate_wpm(self):
        self.assertEqual(calculate_wpm(chars_typed=100, time_elapsed_seconds=30), 40)
        self.assertEqual(calculate_wpm(chars_typed=25, time_elapsed_seconds=6), 50)
        self.assertEqual(calculate_wpm(chars_typed=0, time_elapsed_seconds=10), 0)
        self.assertEqual(calculate_wpm(chars_typed=50, time_elapsed_seconds=0), 0)
        self.assertEqual(calculate_wpm(chars_typed=123, time_elapsed_seconds=25.5), 58)

    def test_calculate_accuracy(self):
        # Perfect accuracy
        self.assertEqual(calculate_accuracy(target_len=100, errors=0), 100.0)
        # Some errors
        self.assertEqual(calculate_accuracy(target_len=100, errors=5), 95.0)
        # Rounding check
        self.assertEqual(
            calculate_accuracy(target_len=30, errors=1), 96.7
        )  # (29/30)*100 = 96.666 -> 96.7
        # Zero length target
        self.assertEqual(calculate_accuracy(target_len=0, errors=0), 0.0)
        self.assertEqual(calculate_accuracy(target_len=0, errors=5), 0.0)
        # More errors than length (should cap at 0%)
        self.assertEqual(calculate_accuracy(target_len=50, errors=60), 0.0)
        # All errors
        self.assertEqual(calculate_accuracy(target_len=50, errors=50), 0.0)


if __name__ == "__main__":
    unittest.main()
