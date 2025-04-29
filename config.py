"""
Configuration constants for the Typing Test application.
"""

import curses

# Key Codes
ESCAPE_KEY = 27
BACKSPACE_CODES = [curses.KEY_BACKSPACE, 127, 8, ord("\b")]

# File Paths
RESULTS_FILENAME = "typing_results.txt"
DEFAULT_WORD_LIST_FOLDER = "word_lists"

# Add other constants here if needed (e.g., API URL if you bring it back)
