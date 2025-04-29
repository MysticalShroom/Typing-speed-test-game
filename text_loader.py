"""
Contains the abstract base class for text loading and concrete implementations.
"""

from abc import ABC, abstractmethod
import os
import random


class TextLoader(ABC):
    """Abstract base class for loading text for the typing test."""

    def __init__(self, difficulty: str = "medium", word_count: int = 25):
        # Store common attributes, even if not used by all subclasses
        self.difficulty = difficulty
        self.word_count = word_count

    @abstractmethod
    def load(self) -> str:
        """Load and return text string according to implementation."""
        pass

    # Optional: Allow changing difficulty/count after initialization
    def set_options(self, difficulty: str, word_count: int):
        """Updates the difficulty and word count for the next load."""
        self.difficulty = difficulty
        self.word_count = word_count


class LocalFolderWordLoader(TextLoader):
    """Loads words from text files within a specified local folder."""

    def __init__(
        self, folder_path: str, difficulty: str = "medium", word_count: int = 25
    ):
        """
        Initializes the loader by reading words from files in the folder.
        Assumes files named 'easy.txt', 'medium.txt', 'hard.txt' exist.
        """
        super().__init__(difficulty, word_count)  # Initialize base class attributes
        self.folder_path = folder_path
        self.words_by_difficulty: dict[str, list[str]] = self._read_words_from_files()

        if not any(self.words_by_difficulty.values()):
            # Raise an error if no words could be loaded at all
            raise FileNotFoundError(
                f"No word files found or files are empty in '{self.folder_path}'. "
                "Expected easy.txt, medium.txt, hard.txt."
            )

    def _read_words_from_files(self) -> dict[str, list[str]]:
        """Reads words from easy.txt, medium.txt, hard.txt in the folder."""
        word_map = {"easy": [], "medium": [], "hard": []}
        expected_files = {
            "easy": "easy.txt",
            "medium": "medium.txt",
            "hard": "hard.txt",
        }
        print(f"Attempting to load words from: {self.folder_path}")
        for diff_level, filename in expected_files.items():
            file_path = os.path.join(self.folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    words = [line.strip().lower() for line in f if line.strip()]
                    word_map[diff_level] = words
                    print(f"  - Loaded {len(words)} words from '{filename}'.")
            except FileNotFoundError:
                print(f"  - Warning: File not found: '{file_path}'")
            except IOError as e:
                print(f"  - Error reading file '{file_path}': {e}")
            except Exception as e:
                print(f"  - Unexpected error processing file '{file_path}': {e}")
        return word_map

    def load(self) -> str:
        """
        Loads the required number of words for the current difficulty.

        Selects words randomly. For 'random' difficulty, it uses words
        from all loaded lists combined.
        """
        word_list = []  # Initialize empty list

        # <<< Add logic for "random" difficulty >>>
        if self.difficulty == "random":
            # Combine words from all difficulty lists
            combined_list = []
            for key in self.words_by_difficulty:
                combined_list.extend(self.words_by_difficulty[key])
            # Remove duplicates if desired (optional)
            # combined_list = list(set(combined_list))
            word_list = combined_list
            print(
                f"Info: Using combined list of {len(word_list)} words "
                f"for 'random' difficulty."
            )
        else:
            # Original logic for easy, medium, hard
            word_list = self.words_by_difficulty.get(self.difficulty, [])

        # --- Common logic for sampling from the selected word_list ---
        if not word_list:
            print(f"Error: No words available for difficulty '{self.difficulty}'.")
            return ""

        available_count = len(word_list)
        count_to_sample = min(self.word_count, available_count)

        if count_to_sample == 0:
            print(f"Error: No words to sample for difficulty '{self.difficulty}'.")
            return ""
        if count_to_sample < self.word_count:
            print(
                f"Warning: Only {available_count} words available for "
                f"'{self.difficulty}', using {count_to_sample}."
            )

        try:
            selected_words = random.sample(word_list, count_to_sample)
            return " ".join(selected_words)
        except ValueError as e:
            print(f"Error sampling words: {e}")
            return ""
