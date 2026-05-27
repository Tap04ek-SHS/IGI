"""
Purpose: Laboratory Work 3
Title: Standard data types, collections, functions, modules
Version: 1.0
Author: [Журавский Г.И.]
Date: 2026-04-14
"""

def error_handler(func):
    """
    Decorator to handle specific exceptions such as ValueError and ZeroDivisionError.
    Demonstrates Requirement 10 and 12.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"\n[Error] Invalid value: {e}")
        except ZeroDivisionError as e:
            print(f"\n[Error] Division by zero occurred: {e}")
        except Exception as e:
            print(f"\n[Error] An unexpected error occurred: {e}")
    return wrapper

def get_int_input(prompt: str) -> int:
    """Safely gets an integer input from the user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a whole integer.")

def get_float_input(prompt: str) -> float:
    """Safely gets a float input from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a floating-point number.")