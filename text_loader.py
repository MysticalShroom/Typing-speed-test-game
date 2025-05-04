from abc import ABC, abstractmethod
import os
import random
import requests

API_URL = "https://random-word-api.vercel.app/api?words=50"


class TextLoader(ABC):
    def __init__(self, difficulty: str = "medium", word_count: int = 25):
        self.difficulty = difficulty
        self.word_count = word_count

    @abstractmethod
    def load(self) -> str:
        pass

    def set_options(self, difficulty: str, word_count: int):
        self.difficulty = difficulty
        self.word_count = word_count


class ApiWordLoader(TextLoader):
    def __init__(self, difficulty: str = "medium", word_count: int = 25):
        super().__init__(difficulty, word_count)
        print("Attempting to fetch words from API...")
        self._fetched_from_api = False
        self.all_words: list[str] | None = self._fetch_words()
        if not self.all_words:
            print("Warning: API fetch failed. Using fallback list.")
            self.all_words = self._get_fallback_words()
            print(
                f"Word source ready: Using Fallback list ({len(self.all_words)} words)."
            )
        else:
            print(f"Word source ready: Using API list ({len(self.all_words)} words).")

    def _fetch_words(self) -> list[str] | None:
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            word_list = None
            if isinstance(data, list) and data:
                word_list = data
            if word_list:
                unique_words = list(
                    set(
                        w.lower()
                        for w in word_list
                        if isinstance(w, str) and w.isalpha()
                    )
                )
                if unique_words:
                    self._fetched_from_api = True
                    return unique_words
            print(f"  - Warning: API data not a valid list ({type(data)}).")
            return None
        except requests.exceptions.Timeout:
            print("  - API request timed out.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  - API request failed: {e}")
            return None
        except Exception as e:
            print(f"  - Error fetching words: {e}")
            return None

    def _get_fallback_words(self) -> list[str]:
        return [
            "the",
            "quick",
            "brown",
            "fox",
            "jumps",
            "over",
            "lazy",
            "dog",
            "python",
            "coding",
            "terminal",
            "keyboard",
            "practice",
            "speed",
            "accuracy",
            "challenge",
            "developer",
            "language",
            "program",
            "function",
            "variable",
            "interface",
            "exception",
            "algorithm",
        ]

    def _filter_words(self, word_list: list[str]) -> list[str]:
        if self.difficulty == "easy":
            return [w for w in word_list if 3 <= len(w) <= 4]
        elif self.difficulty == "medium":
            return [w for w in word_list if 5 <= len(w) <= 7]
        elif self.difficulty == "hard":
            return [w for w in word_list if len(w) >= 8]
        elif self.difficulty == "random":
            return word_list
        else:
            return word_list

    def load(self) -> str:
        filtered_list = self._filter_words(self.all_words)

        if not filtered_list:
            difficulty_msg = (
                f"'{self.difficulty}'" if self.difficulty != "random" else "any"
            )
            print(f"Error: No words found matching {difficulty_msg} criteria.")
            return ""

        available_count = len(filtered_list)
        count_to_sample = min(self.word_count, available_count)

        if count_to_sample <= 0:
            print(f"Error: No words to sample for difficulty '{self.difficulty}'.")
            return ""
        if count_to_sample < self.word_count and available_count < self.word_count:
            print(
                f"Warning: Only {available_count} words matching criteria for "
                f"'{self.difficulty}', using {count_to_sample}."
            )

        try:
            selected_words = random.sample(filtered_list, count_to_sample)
            return " ".join(selected_words)
        except ValueError as e:
            print(f"Error sampling words: {e}")
            return ""


class LocalFolderWordLoader(TextLoader):
    def __init__(
        self, folder_path: str, difficulty: str = "medium", word_count: int = 25
    ):
        super().__init__(difficulty, word_count)
        self.folder_path = folder_path
        self.words_by_difficulty: dict[str, list[str]] = self._read_words_from_files()
        if not any(self.words_by_difficulty.values()):
            raise FileNotFoundError(
                f"No word files found or files are empty in '{self.folder_path}'. "
                "Expected easy.txt, medium.txt, hard.txt."
            )
        print(f"Word source ready: Loaded words from folder '{self.folder_path}'.")

    def _read_words_from_files(self) -> dict[str, list[str]]:
        word_map = {"easy": [], "medium": [], "hard": []}
        expected_files = {
            "easy": "easy.txt",
            "medium": "medium.txt",
            "hard": "hard.txt",
        }
        print(f"Attempting to load words from folder: {self.folder_path}")
        for diff_level, filename in expected_files.items():
            file_path = os.path.join(self.folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    words = [
                        line.strip().lower()
                        for line in f
                        if line.strip() and line.strip().isalpha()
                    ]
                    word_map[diff_level] = list(set(words))
                    count = len(word_map[diff_level])
                    print(f"  - Loaded {count} words from '{filename}'.")
            except FileNotFoundError:
                print(f"  - Warning: File not found: '{file_path}'")
            except IOError as e:
                print(f"  - Error reading file '{file_path}': {e}")
            except Exception as e:
                print(f"  - Unexpected error processing file '{file_path}': {e}")
        return word_map

    def load(self) -> str:
        word_list = []
        if self.difficulty == "random":
            for key in self.words_by_difficulty:
                word_list.extend(self.words_by_difficulty[key])
            word_list = list(set(word_list))
            print(f"Info: Using combined list ({len(word_list)} words) for 'random'.")
        else:
            word_list = self.words_by_difficulty.get(self.difficulty, [])

        if not word_list:
            print(f"Error: No words available for difficulty '{self.difficulty}'.")
            return ""

        available_count = len(word_list)
        count_to_sample = min(self.word_count, available_count)

        if count_to_sample <= 0:
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
