import curses
from curses import wrapper
import os
import traceback

from config import RESULTS_FILENAME, USE_API_LOADER, DEFAULT_WORD_LIST_FOLDER

from text_loader import ApiWordLoader, LocalFolderWordLoader
from typing_test import TypingTest


def main(stdscr):
    curses.curs_set(0)
    loader = None

    try:
        if USE_API_LOADER:
            print("Config set to use API Loader.")
            loader = ApiWordLoader()
            if not loader.all_words:
                raise RuntimeError(
                    "API Loader failed to get any words (API & Fallback)."
                )

        else:
            folder_path = DEFAULT_WORD_LIST_FOLDER
            print(f"Config set to use Local Folder Loader ('{folder_path}').")

            if not os.path.isdir(folder_path):
                raise FileNotFoundError(
                    f"Word list folder not found: '{folder_path}'. "
                    "Please create it and add easy.txt, medium.txt, hard.txt, "
                    "or set USE_API_LOADER = True in config.py."
                )

            loader = LocalFolderWordLoader(folder_path=folder_path)

        if loader:
            test = TypingTest(stdscr, loader)
            test.start()
        else:
            raise RuntimeError("Failed to initialize a word loader.")

    except FileNotFoundError as e:
        if not curses.isendwin():
            curses.endwin()
        print(f"\nConfiguration Error: {e}")
    except RuntimeError as e:
        if not curses.isendwin():
            curses.endwin()
        print(f"\nRuntime Error: {e}")
    except SystemExit:
        pass
    except curses.error:
        if not curses.isendwin():
            curses.endwin()
        print("\nA curses error occurred:")
        traceback.print_exc()
    except Exception:
        if not curses.isendwin():
            curses.endwin()
        print("\nAn unexpected error occurred:")
        traceback.print_exc()


if __name__ == "__main__":
    if USE_API_LOADER:
        try:
            import requests  # noqa: F401
        except ImportError:
            print("ERROR: Configured to use API, but 'requests' is not installed.")
            print("Please install it: pip install requests")
            exit()

    try:
        wrapper(main)
    except Exception:
        print("\nA critical error occurred:")
        traceback.print_exc()
    finally:
        print(
            f"\nApplication closed. Results saved in '{RESULTS_FILENAME}' "
            "(if any tests were completed)."
        )
