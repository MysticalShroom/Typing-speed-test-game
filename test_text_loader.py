# test_text_loader.py
import unittest
from unittest.mock import patch  # <<< Import patch

# Import the class we want to test (make sure text_loader.py is accessible)
from text_loader import LocalFolderWordLoader

# Dummy folder path for initialization (won't actually be used due to mock)
DUMMY_FOLDER_PATH = "dummy_test_words"


class TestLocalFolderWordLoader(unittest.TestCase):
    """Tests for the LocalFolderWordLoader class."""

    def setUp(self):
        """Set up sample word data and mock file reading."""
        self.sample_words = {
            "easy": ["cat", "dog", "sun", "run", "fly", "car"],
            "medium": [
                "python",
                "coding",
                "simple",
                "medium",
                "words",
                "sample",
                "testing",
            ],
            "hard": [
                "algorithm",
                "interface",
                "recursion",
                "database",
                "structure",
                "application",
                "inheritance",
                "polymorphism",
            ],
        }

        patcher = patch("text_loader.LocalFolderWordLoader._read_words_from_files")

        self.mock_read_files = patcher.start()

        self.mock_read_files.return_value = self.sample_words

        self.addCleanup(patcher.stop)

        self.loader = LocalFolderWordLoader(folder_path=DUMMY_FOLDER_PATH)

    def test_load_specific_difficulty_correct_count(self):
        """Test loading a specific number of words for a standard difficulty."""
        self.loader.set_options(difficulty="medium", word_count=5)
        loaded_text = self.loader.load()
        loaded_words = loaded_text.split()
        self.assertEqual(len(loaded_words), 5)
        for word in loaded_words:
            self.assertIn(word, self.sample_words["medium"])

    def test_load_more_words_than_available(self):
        """Test loading when requesting more words than available."""
        self.loader.set_options(difficulty="easy", word_count=10)
        loaded_text = self.loader.load()
        loaded_words = loaded_text.split()
        self.assertEqual(len(loaded_words), 6)
        self.assertCountEqual(loaded_words, self.sample_words["easy"])

    def test_load_random_difficulty(self):
        """Test loading words for the 'random' difficulty."""
        self.loader.set_options(difficulty="random", word_count=8)
        loaded_text = self.loader.load()
        loaded_words = loaded_text.split()
        all_sample_words = (
            self.sample_words["easy"]
            + self.sample_words["medium"]
            + self.sample_words["hard"]
        )
        self.assertEqual(len(loaded_words), 8)
        for word in loaded_words:
            self.assertIn(word, all_sample_words)

    def test_load_zero_word_count(self):
        """Test loading when word_count is 0."""
        self.loader.set_options(difficulty="medium", word_count=0)
        loaded_text = self.loader.load()
        self.assertEqual(loaded_text, "")
        self.assertEqual(
            len(loaded_text.split()), 0 if not loaded_text else len(loaded_text.split())
        )

    def test_load_invalid_difficulty(self):
        """Test loading with a difficulty level that has no *mocked* words."""

        self.loader.set_options(difficulty="nonexistent", word_count=5)
        loaded_text = self.loader.load()
        self.assertEqual(loaded_text, "")

    def test_load_random_difficulty_empty_source(self):
        """Test 'random' difficulty when source lists are empty by overwriting mock."""

        self.loader.words_by_difficulty = {"easy": [], "medium": [], "hard": []}
        self.loader.set_options(difficulty="random", word_count=5)
        loaded_text = self.loader.load()
        self.assertEqual(loaded_text, "")


if __name__ == "__main__":
    unittest.main()
