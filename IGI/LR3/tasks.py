"""
Purpose: Laboratory Work 3
Title: Standard data types, collections, functions, modules
Version: 1.0
Author:[Журавский Г.И.]
Date: 2026-04-15
"""
import math


def calculate_taylor_series(x: float, eps: float) -> tuple:
    """
    Task 1: Calculates ln(1+x) using Taylor series expansion.
    Returns the number of terms, calculated value, and math module value.
    """
    if not (-1 < x < 1):
        raise ValueError("x must be strictly between -1 and 1 for convergence.")

    n = 1
    term = x
    sum_series = 0.0
    max_iter = 500

    while abs(term) >= eps and n <= max_iter:
        sum_series += term
        n += 1
        term = ((-1) ** (n - 1) * (x ** n)) / n

    math_val = math.log(1 + x)
    return n - 1, sum_series, math_val


def is_octal_number(s: str) -> bool:
    """
    Task 3: Determines if the string is a valid octal number without using regex.
    """
    s = s.strip()
    if not s:
        return False

    # Check for optional sign
    if s[0] in ('-', '+'):
        s = s[1:]
        if not s:
            return False

    for char in s:
        if char not in "01234567":
            return False
    return True


def analyze_string_task4(text: str) -> dict:
    """
    Task 4: Analyzes the string: counts words, finds shortest 'i' word,
    and finds repeating words. No regular expressions are used.
    """
    # Clean text from punctuation that separates words (commas, dots)
    cleaned = text.replace(',', ' ').replace('.', ' ')
    words = cleaned.split()

    # a) Words with odd number of letters
    total_words = len(words)
    odd_length_words = [w for w in words if len(w) % 2 != 0]

    # b) Shortest word starting with 'i' (case-insensitive search)
    i_words = [w for w in words if w.lower().startswith('i')]
    shortest_i_word = min(i_words, key=len) if i_words else None

    # c) Repeating words
    words_lower = [w.lower() for w in words]
    repeating_words = list(set([w for w in words_lower if words_lower.count(w) > 1]))

    return {
        "total_words": total_words,
        "odd_length_words": odd_length_words,
        "shortest_i_word": shortest_i_word,
        "repeating_words": repeating_words
    }


def process_list_task5(lst: list) -> tuple:
    """
    Task 5: Calculates the sum of elements with odd positions (indices 0, 2, 4...)
    and the sum of elements located between the first and last negative elements.
    """
    # Assuming "нечетные номера" (odd positions like 1st, 3rd, 5th)
    # corresponds to even Python indices (0, 2, 4...)
    sum_odd_positions = sum(lst[0::2])

    first_neg = -1
    last_neg = -1

    for i, val in enumerate(lst):
        if val < 0:
            if first_neg == -1:
                first_neg = i
            last_neg = i

    sum_between = 0.0
    # Process only if we found at least two distinct negative elements
    if first_neg != -1 and last_neg != -1 and first_neg != last_neg:
        sum_between = sum(lst[first_neg + 1: last_neg])

    return sum_odd_positions, sum_between