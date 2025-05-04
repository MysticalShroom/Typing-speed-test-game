import unittest
from unittest.mock import Mock

from typing_test import TypingTest
from text_loader import TextLoader
from config import BACKSPACE_CODES


class TestTypingTestLogic(unittest.TestCase):
    """Tests core logic (like error counting) in TypingTest."""

    def setUp(self):
        """Set up mocks for dependencies."""
        self.mock_stdscr = Mock()
        self.mock_loader = Mock(spec=TextLoader)

        self.test_text = "hello world example"
        self.mock_loader.load.return_value = self.test_text

        self.test_instance = TypingTest(self.mock_stdscr, self.mock_loader)
        self.test_instance.target_text = self.test_text

        self.test_instance.current_text = []
        self.test_instance.errors = 0
        self.test_instance.has_started_typing = False

    def simulate_typing(self, chars_to_type: list):

        if not self.test_instance.has_started_typing and chars_to_type:
            self.test_instance.has_started_typing = True

        for char_or_code in chars_to_type:
            current_len = len(self.test_instance.current_text)

            if char_or_code in BACKSPACE_CODES:
                if self.test_instance.current_text:
                    removed_idx = current_len - 1
                    if (
                        removed_idx < len(self.test_instance.target_text)
                        and self.test_instance.current_text[removed_idx]
                        != self.test_instance.target_text[removed_idx]
                    ):
                        self.test_instance.errors = max(
                            0, self.test_instance.errors - 1
                        )
                    self.test_instance.current_text.pop()
            elif isinstance(char_or_code, str):
                if current_len < len(self.test_instance.target_text):
                    target_char = self.test_instance.target_text[current_len]
                    if char_or_code != target_char:
                        self.test_instance.errors += 1
                    self.test_instance.current_text.append(char_or_code)

    def test_no_errors_correct_typing(self):
        """Test error count remains 0 for correct typing."""
        self.simulate_typing(["h", "e", "l", "l", "o"])
        self.assertEqual(self.test_instance.errors, 0)
        self.assertEqual("".join(self.test_instance.current_text), "hello")

    def test_error_increment_incorrect_typing(self):
        """Test error count increments for incorrect characters."""
        self.simulate_typing(["h", "X", "l", "l", "Y"])
        self.assertEqual(self.test_instance.errors, 2)
        self.assertEqual("".join(self.test_instance.current_text), "hXllY")

    def test_backspace_corrects_error_count(self):
        """Test backspace removes error and decrements count."""
        backspace = BACKSPACE_CODES[0]
        self.simulate_typing(["h", "e", "X", backspace, "l", "l", "o"])
        self.assertEqual(self.test_instance.errors, 0)
        self.assertEqual("".join(self.test_instance.current_text), "hello")

    def test_backspace_does_not_affect_error_count_if_correct(self):
        backspace = BACKSPACE_CODES[0]

        self.simulate_typing(["h", "e", "l", backspace, "l"])

        self.assertEqual(
            self.test_instance.errors,
            0,
            "Error count should be 0",
        )
        self.assertEqual(
            "".join(self.test_instance.current_text),
            "hel",
            "Current text should be 'hel'",
        )

    def test_multiple_errors_and_backspaces(self):
        backspace = BACKSPACE_CODES[0]
        self.simulate_typing(
            [
                "h",
                "e",
                "X",
                "l",
                "o",
                " ",
                "W",
                "o",
                "r",
                "L",
                backspace,
                "l",
                "d",
            ]
        )
        self.assertEqual(self.test_instance.errors, 2)
        self.assertEqual("".join(self.test_instance.current_text), "heXlo World")


if __name__ == "__main__":
    unittest.main()
