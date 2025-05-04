def calculate_wpm(chars_typed: int, time_elapsed_seconds: float) -> int:
    """Calculates Words Per Minute (WPM)."""
    if time_elapsed_seconds <= 0:
        return 0
    wpm_raw = (chars_typed / 5) / (time_elapsed_seconds / 60)
    return round(wpm_raw)


def calculate_accuracy(target_len: int, errors: int) -> float:
    """Calculates typing accuracy percentage."""
    if target_len <= 0:
        return 0.0
    actual_errors = min(errors, target_len)
    correct_chars = target_len - actual_errors
    accuracy = (correct_chars / target_len) * 100
    return round(accuracy, 1)
