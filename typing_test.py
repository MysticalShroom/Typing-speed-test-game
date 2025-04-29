# typing_test.py
"""
Contains the main TypingTest class for managing the application UI and logic.
"""
import curses
import time  # Still needed for time.time()
from datetime import datetime


# Import necessary components from other modules
from text_loader import TextLoader  # Import the ABC

# Import constants directly
from config import RESULTS_FILENAME, ESCAPE_KEY, BACKSPACE_CODES
from utils import calculate_wpm, calculate_accuracy


class TypingTest:
    """Manages the Typing Speed Test application using curses."""

    def __init__(self, stdscr, text_loader: TextLoader):
        """Initializes the TypingTest application."""
        self.stdscr = stdscr
        self.text_loader = text_loader
        self.target_text: str = ""
        self.current_text: list[str] = []
        self.wpm: int = 0
        self.start_time: float = 0.0
        self.word_count: int = getattr(text_loader, "word_count", 25)
        self.difficulty: str = getattr(text_loader, "difficulty", "medium")
        self.has_started_typing: bool = False
        self.errors: int = 0

    def _show_difficulty_screen(self) -> str:
        """Displays the difficulty selection screen and returns the choice."""
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Select difficulty:")
        self.stdscr.addstr(2, 0, "1. Easy")
        self.stdscr.addstr(3, 0, "2. Medium")
        self.stdscr.addstr(4, 0, "3. Hard")
        self.stdscr.addstr(5, 0, "4. Random (Mixed Lengths)")
        self.stdscr.addstr(7, 0, "Press 1, 2, 3, or 4 (ESC to quit): ")
        self.stdscr.refresh()
        while True:
            try:
                key = self.stdscr.getkey()
                if key in ("1", "2", "3", "4"):
                    difficulties = ["easy", "medium", "hard", "random"]
                    return difficulties[int(key) - 1]
                # Use isinstance for type safety before ord()
                elif isinstance(key, str) and len(key) == 1 and ord(key) == ESCAPE_KEY:
                    raise SystemExit()
            except (TypeError, ValueError, curses.error, SystemExit) as e:
                if isinstance(e, SystemExit):
                    raise
                self.stdscr.clear()
                # Simplified redraw on error
                self.stdscr.addstr(0, 0, "Select difficulty (error/resized?):")
                self.stdscr.addstr(6, 0, "Press 1, 2, 3, or 4 (ESC to quit): ")
                self.stdscr.refresh()
                continue

    def _show_word_count_screen(self) -> int:
        """Displays the word count input screen and returns the value."""
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "How many words? (5-50)")
        prompt = "Enter number (ESC to quit): "
        prompt_row = 2
        self.stdscr.addstr(prompt_row, 0, prompt)
        self.stdscr.refresh()
        input_str = ""
        input_start_col = len(prompt)
        curses.curs_set(1)
        while True:
            try:
                self.stdscr.move(prompt_row, input_start_col + len(input_str))
                key_code = self.stdscr.getch()
                if key_code == ESCAPE_KEY:
                    raise SystemExit()
                elif key_code == curses.KEY_ENTER or key_code in [10, 13]:
                    break
                elif key_code in BACKSPACE_CODES:
                    if input_str:
                        input_str = input_str[:-1]
                        y, x = self.stdscr.getyx()
                        if x > input_start_col:
                            self.stdscr.move(y, x - 1)
                            self.stdscr.delch()
                # Check ASCII range for digits '0' to '9'
                elif 48 <= key_code <= 57:
                    if len(input_str) < 2:  # Max 2 digits
                        input_str += chr(key_code)
                        self.stdscr.addch(key_code)  # Manual echo
                self.stdscr.refresh()
            except curses.error:
                # Simplified redraw on error
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, "How many words? (5-50) (resized?)")
                self.stdscr.addstr(prompt_row, 0, prompt + input_str)
                self.stdscr.refresh()
                continue
            except SystemExit:
                raise
            except Exception:  # Catch any other unexpected error
                continue  # Ignore and let user try again
        curses.curs_set(0)
        try:
            word_count = int(input_str) if input_str else 25
        except ValueError:
            word_count = 25
        return max(5, min(50, word_count))

    def start(self):
        """Starts the main application loop."""
        try:
            self._init_colors()
        except RuntimeError as e:
            print(f"Error: {e}")
            return

        while True:
            try:
                self.difficulty = self._show_difficulty_screen()
                self.word_count = self._show_word_count_screen()
            except SystemExit:
                break

            if hasattr(self.text_loader, "set_options"):
                self.text_loader.set_options(self.difficulty, self.word_count)
            else:
                self.text_loader.difficulty = self.difficulty
                self.text_loader.word_count = self.word_count

            self.target_text = self.text_loader.load()

            if not self.target_text:
                self._display_error("Error: Could not load text from loader.")
                break

            try:
                self._show_start_screen()
            except SystemExit:
                break

            while True:  # Inner retry loop
                self.current_text = []
                self.wpm = 0
                self.start_time = 0.0
                self.has_started_typing = False
                self.errors = 0
                try:
                    self._run_test()
                    should_retry_same = self._prompt_retry()
                    if not should_retry_same:
                        break
                except SystemExit:
                    return  # Exit app cleanly
                except curses.error:
                    # Attempt to display error within curses if possible
                    self._display_error("A window error occurred.")
                    return  # Exit application

    def _init_colors(self):
        """Initializes color pairs."""
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_RED, -1)
            curses.init_pair(3, curses.COLOR_WHITE, -1)
            curses.init_pair(4, curses.COLOR_CYAN, -1)
            curses.init_pair(5, curses.COLOR_YELLOW, -1)
        except curses.error as e:
            # Raise a runtime error that main can potentially catch
            raise RuntimeError(f"Color setup failed: {e}.") from e
        except Exception as e:
            # Catch other potential init errors
            raise RuntimeError(f"Color setup failed unexpectedly: {e}") from e

    def _show_start_screen(self):
        """Displays the welcome screen before a test starts."""
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Welcome!", curses.color_pair(3))
        self.stdscr.addstr(
            1, 0, f"Difficulty: {self.difficulty.capitalize()}", curses.color_pair(4)
        )
        self.stdscr.addstr(2, 0, f"Word count: {self.word_count}", curses.color_pair(4))
        self.stdscr.addstr(4, 0, "Press any key to begin!", curses.color_pair(3))
        self.stdscr.refresh()
        try:
            self.stdscr.nodelay(False)  # Blocking wait
            self.stdscr.getkey()
        except curses.error:
            # If error happens waiting for key (e.g. resize), exit gracefully
            self._display_error("Input error before start. Exiting.")
            # _display_error now raises SystemExit

    def _display_test_ui(self, time_elapsed: float):
        """Displays the main typing test interface."""
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        start_row = 3

        try:  # Draw Headers (broken long lines)
            diff_str = f"Diff: {self.difficulty.capitalize()}"
            word_str = f"Words: {self.word_count}"
            err_str = f"Errors: {self.errors}"
            time_val = (
                f"{int(time_elapsed)}s" if self.has_started_typing else "Waiting..."
            )
            time_str_display = f"Time: {time_val}"
            wpm_str_display = (
                f"WPM: {self.wpm}" if self.has_started_typing else "WPM: 0"
            )
            # Line 0
            self.stdscr.addstr(0, 0, diff_str, curses.color_pair(4))
            col_after_diff = len(diff_str) + 2
            if col_after_diff + len(word_str) < max_x:
                self.stdscr.addstr(0, col_after_diff, word_str, curses.color_pair(4))
            # Line 1
            self.stdscr.addstr(1, 0, time_str_display, curses.color_pair(4))
            errors_start_pos = len(time_str_display) + 2
            if errors_start_pos + len(err_str) < max_x:
                self.stdscr.addstr(1, errors_start_pos, err_str, curses.color_pair(5))
            wpm_start_pos = errors_start_pos + len(err_str) + 2
            if wpm_start_pos + len(wpm_str_display) < max_x:
                self.stdscr.addstr(
                    1, wpm_start_pos, wpm_str_display, curses.color_pair(3)
                )
        except curses.error:
            pass  # Ignore drawing errors if window too small

        # --- Display target/typed text ---
        cursor_y, cursor_x = start_row, 0
        if self.target_text:
            line_y, line_x = start_row, 0
            for i, target_char in enumerate(self.target_text):
                if line_x >= max_x:
                    line_y, line_x = line_y + 1, 0
                if line_y >= max_y:
                    break
                display_char, color_pair_num = target_char, 3  # Defaults
                if i < len(self.current_text):
                    typed_char = self.current_text[i]
                    display_char = typed_char
                    color_pair_num = 1 if typed_char == target_char else 2
                elif i == len(self.current_text):
                    cursor_y, cursor_x = line_y, line_x
                try:
                    if line_y < max_y and line_x < max_x:
                        self.stdscr.addstr(
                            line_y,
                            line_x,
                            display_char,
                            curses.color_pair(color_pair_num),
                        )
                except curses.error:
                    pass
                line_x += 1
            if len(self.current_text) == len(self.target_text):  # Final cursor pos
                if line_x >= max_x:
                    line_y += 1
                    line_x = 0
                if line_y < max_y:
                    cursor_y, cursor_x = line_y, line_x

        # --- Move cursor ---
        is_test_finished = len(self.current_text) == len(self.target_text)
        if not is_test_finished and cursor_y < max_y and cursor_x < max_x:
            try:
                self.stdscr.move(cursor_y, cursor_x)
            except curses.error:
                pass
        self.stdscr.refresh()

    def _run_test(self):
        """Runs the main typing test loop."""
        if not self.target_text:
            raise ValueError("Target text is empty.")
        self.stdscr.nodelay(True)
        curses.curs_set(1)
        while True:
            current_time = time.time()
            time_elapsed = 0.0
            if self.has_started_typing:
                time_elapsed = max(0.1, current_time - self.start_time)
                self.wpm = calculate_wpm(len(self.current_text), time_elapsed)
            else:
                self.wpm = 0

            try:
                self._display_test_ui(time_elapsed)
            except curses.error:
                pass

            if len(self.current_text) == len(self.target_text):
                self.stdscr.nodelay(False)
                curses.curs_set(0)
                break

            try:
                key_code = self.stdscr.getch()
                if key_code == -1:
                    time.sleep(0.01)
                    continue
                key = chr(key_code) if 32 <= key_code <= 126 else key_code
            except curses.error:
                time.sleep(0.01)
                continue

            is_printable = isinstance(key, str)
            if (
                not self.has_started_typing
                and is_printable
                and key_code != ESCAPE_KEY
                and key_code not in BACKSPACE_CODES
            ):
                self.has_started_typing = True
                self.start_time = time.time()

            if key_code == ESCAPE_KEY:
                raise SystemExit()

            if key_code in BACKSPACE_CODES:
                if self.current_text:
                    removed_idx = len(self.current_text) - 1
                    if (
                        removed_idx < len(self.target_text)
                        and self.current_text[removed_idx]
                        != self.target_text[removed_idx]
                    ):
                        self.errors = max(0, self.errors - 1)
                    self.current_text.pop()
            elif is_printable:
                if len(self.current_text) < len(self.target_text):
                    target_char = self.target_text[len(self.current_text)]
                    if key != target_char:
                        self.errors += 1
                    self.current_text.append(key)

    def _save_results_to_file(
        self, wpm: int, accuracy: float, time_taken: float, errors: int
    ):
        """Saves the test results to a plain text file."""
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Break long f-string
        result_line = (
            f"Timestamp: {timestamp_str}, Difficulty: {self.difficulty.capitalize()}, "
            f"Word count: {self.word_count}, WPM: {wpm}, "
            f"Accuracy: {accuracy}%, Errors: {errors}, Time: {int(time_taken)}"
        )
        try:
            # Ensure RESULTS_FILENAME is imported or defined
            with open(RESULTS_FILENAME, "a", encoding="utf-8") as f:
                f.write(result_line + "\n")
        except (IOError, OSError) as e:
            # Consider logging this error instead of printing if it interferes
            # But print is fine for now, visible after exit
            print(f"\nError writing results: {e}")
        except Exception as e:
            print(f"\nUnexpected error writing results: {e}")

    def _prompt_retry(self) -> bool:
        """Displays results, saves them, asks action."""
        time_taken = time.time() - self.start_time if self.has_started_typing else 0.0
        accuracy = 0.0
        target_len = len(self.target_text)
        if target_len > 0:
            accuracy = calculate_accuracy(target_len, self.errors)

        final_wpm = self.wpm
        self._save_results_to_file(final_wpm, accuracy, time_taken, self.errors)

        max_y, max_x = self.stdscr.getmaxyx()
        num_text_lines = 0
        start_row_text = 3
        if target_len > 0 and max_x > 1:
            num_text_lines = (target_len + max_x - 1) // max_x
        # Ensure at least 3 lines below text area for results/prompt
        results_start_row = min(max_y - 3, start_row_text + num_text_lines + 1)

        for r in range(results_start_row, max_y):  # Clear result area
            try:
                self.stdscr.move(r, 0)
                self.stdscr.clrtoeol()
            except curses.error:
                pass

        # Place prompt just below results line
        prompt_row = results_start_row + 2

        try:
            title = "--- Test Complete! ---"
            # Break potentially long results line
            res_line1 = (
                f"WPM: {final_wpm} | Accuracy: {accuracy}% ({self.errors} err) | "
                f"Time: {int(time_taken)}s"
            )
            prompt = "R: Retry | N: New Test | Any key: Quit"

            self.stdscr.addstr(results_start_row, 0, title, curses.A_BOLD)
            # Check bounds before adding result line
            if results_start_row + 1 < max_y:
                self.stdscr.addstr(
                    results_start_row + 1, 0, res_line1, curses.color_pair(3)
                )
            # Check bounds before adding prompt line
            if prompt_row < max_y:
                self.stdscr.addstr(prompt_row, 0, prompt, curses.color_pair(3))
            else:  # Fallback if screen too small
                self.stdscr.addstr(
                    max_y - 1, 0, "R:Retry|N:New|Quit?", curses.color_pair(3)
                )
        except curses.error:
            # Fallback if even drawing results fails
            try:
                self.stdscr.addstr(
                    max_y - 1, 0, "R:Retry|N:New|Quit?", curses.color_pair(3)
                )
            except curses.error:
                pass  # Give up if screen is tiny

        self.stdscr.refresh()

        # --- Get user choice (FIXED F841 logic) ---
        key = ""
        try:
            self.stdscr.nodelay(False)  # Wait for input
            key = self.stdscr.getkey()

            # Process immediately
            if isinstance(key, str):
                key_lower = key.lower()
                if key_lower == "n":
                    return False
                elif key_lower == "r":
                    return True
            # If not a string OR not 'n'/'r', quit
            raise SystemExit()

        except curses.error:
            raise SystemExit()  # Treat curses errors as Quit
        except Exception:
            raise SystemExit()  # Treat other errors as Quit

    def _display_error(self, message: str):
        """Displays an error message and waits for key press to exit."""
        if not curses.isendwin():
            try:
                self.stdscr.nodelay(False)
                self.stdscr.clear()
                # Check bounds before drawing error
                max_y, max_x = self.stdscr.getmaxyx()
                if max_y > 0 and max_x > 0:
                    self.stdscr.addstr(
                        0, 0, message, curses.color_pair(2) | curses.A_BOLD
                    )
                if max_y > 2 and max_x > 0:
                    self.stdscr.addstr(2, 0, "Press any key to exit.")
                self.stdscr.refresh()
                self.stdscr.getkey()  # Wait for key
            except Exception:
                pass  # Ignore errors during error display itself
        raise SystemExit()  # Ensure exit after showing error
