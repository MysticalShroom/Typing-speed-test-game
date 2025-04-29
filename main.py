import curses
from curses import wrapper
import os
import traceback

from config import DEFAULT_WORD_LIST_FOLDER, RESULTS_FILENAME
from text_loader import LocalFolderWordLoader
from typing_test import TypingTest


def main(stdscr):
    """Main function called by curses wrapper."""
    curses.curs_set(0)

    try:
        word_folder_path = DEFAULT_WORD_LIST_FOLDER

        if not os.path.isdir(word_folder_path):
            raise FileNotFoundError(
                f"Word list folder not found: '{word_folder_path}'. "
                "Please create it and add easy.txt, medium.txt, hard.txt."
            )

        loader = LocalFolderWordLoader(folder_path=word_folder_path)
        test = TypingTest(stdscr, loader)

        test.start()

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
        print("\nA unexpected curses error occurred:")
        traceback.print_exc()
    except Exception:
        if not curses.isendwin():
            curses.endwin()
        print("\nAn unexpected error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
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
