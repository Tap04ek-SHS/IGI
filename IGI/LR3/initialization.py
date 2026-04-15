"""
Purpose: Laboratory Work 3
Title: Standard data types, collections, functions, modules
Version: 1.0
Author: [Журавский Г.И.]
Date: 2026-04-15
"""
import random
from utils import get_float_input

def init_with_generator(size: int) -> list:
    """
    Initializes a sequence with random floats using a generator expression.
    """
    return[round(random.uniform(-15.0, 15.0), 2) for _ in range(size)]

def init_with_user_input(size: int) -> list:
    """
    Initializes a sequence using user input from the keyboard.
    """
    return[get_float_input(f"Enter element {i + 1}: ") for i in range(size)]