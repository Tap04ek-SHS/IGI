"""
Purpose: Laboratory Work 3
Title: Standard data types, collections, functions, modules
Version: 1.0
Author: [Журавский Г.И.]
Date: 2026-04-15
"""
from utils import error_handler, get_int_input, get_float_input
from initialization import init_with_generator, init_with_user_input
import tasks


@error_handler
def run_task1():
    """Executes UI logic for Task 1."""
    print("\n--- Task 1: Taylor Series (Variant 13) ---")
    x = get_float_input("Enter x (-1 < x < 1): ")
    eps = get_float_input("Enter precision eps (e.g. 0.001): ")

    n, f_x, math_f_x = tasks.calculate_taylor_series(x, eps)

    print("-" * 65)
    print(f"| {'x':^7} | {'n':^5} | {'F(x)':^15} | {'Math F(x)':^15} | {'eps':^7} |")
    print("-" * 65)
    print(f"| {x:^7.2f} | {n:^5} | {f_x:^15.5f} | {math_f_x:^15.5f} | {eps:^7.5f} |")
    print("-" * 65)


@error_handler
def run_task2():
    """Executes UI logic for Task 2."""
    print("\n--- Task 2: Count Natural Numbers (Variant 13) ---")
    print("Keep entering integers. Enter 0 to stop.")
    count = 0
    while True:
        val = get_int_input("Enter an integer: ")
        if val == 0:
            break
        if val > 0:  # Natural numbers are positive integers > 0
            count += 1
    print(f"Total natural numbers entered: {count}")


@error_handler
def run_task3():
    """Executes UI logic for Task 3."""
    print("\n--- Task 3: Check Octal String (Variant 13) ---")
    s = input("Enter a string to check: ")
    if tasks.is_octal_number(s):
        print(f"--> '{s}' is a VALID octal number.")
    else:
        print(f"--> '{s}' is NOT a valid octal number.")


@error_handler
def run_task4():
    """Executes UI logic for Task 4."""
    print("\n--- Task 4: String Analysis (Variant 13) ---")
    text = ("So she was considering in her own mind, as well as she could, "
            "for the hot day made her feel very sleepy and stupid, whether "
            "the pleasure of making a daisy-chain would be worth the trouble "
            "of getting up and picking the daisies, when suddenly a White "
            "Rabbit with pink eyes ran close by her.")

    print(f"Text to analyze:\n\"{text}\"")
    result = tasks.analyze_string_task4(text)

    print(f"\na) Total words: {result['total_words']}")
    print(f"   Words with odd amount of letters: {', '.join(result['odd_length_words'])}")
    print(f"b) Shortest word starting with 'i': {result['shortest_i_word']}")
    print(f"c) Repeating words (case-insensitive): {', '.join(result['repeating_words'])}")


@error_handler
def run_task5():
    """Executes UI logic for Task 5."""
    print("\n--- Task 5: List Processing (Variant 13) ---")
    size = get_int_input("Enter the size of the list: ")
    if size <= 0:
        raise ValueError("List size must be greater than 0.")

    print("Choose initialization method:")
    print("1. Generator (random numbers)")
    print("2. User input")
    method = get_int_input("Choice: ")

    if method == 1:
        lst = init_with_generator(size)
    elif method == 2:
        lst = init_with_user_input(size)
    else:
        raise ValueError("Invalid initialization method chosen.")

    print(f"\nGenerated list: {lst}")
    sum_odd_pos, sum_between = tasks.process_list_task5(lst)

    print(f"Sum of elements at odd positions: {sum_odd_pos}")
    print(f"Sum of elements between first and last negative elements: {sum_between}")


def main():
    """Main menu loop providing interactive UI."""
    while True:
        print("\n" + "=" * 40)
        print("          LABORATORY WORK 3")
        print("=" * 40)
        print("1. Task 1 (Taylor Series)")
        print("2. Task 2 (Loop & Count Naturals)")
        print("3. Task 3 (Octal String Verification)")
        print("4. Task 4 (String Analysis)")
        print("5. Task 5 (List Math Processing)")
        print("0. Exit")
        print("=" * 40)

        choice = get_int_input("Select a menu option: ")

        if choice == 0:
            print("Exiting the program. Goodbye!")
            break
        elif choice == 1:
            run_task1()
        elif choice == 2:
            run_task2()
        elif choice == 3:
            run_task3()
        elif choice == 4:
            run_task4()
        elif choice == 5:
            run_task5()
        else:
            print("Invalid choice! Please choose a number from 0 to 5.")


if __name__ == "__main__":
    main()