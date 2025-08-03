"""
Mathematical utility functions for the AramGoV2 project.
"""


def add_numbers(a, b):
    """
    Add two numbers together.
    
    Args:
        a (int or float): The first number to add
        b (int or float): The second number to add
    
    Returns:
        int or float: The sum of a and b
    
    Raises:
        TypeError: If either argument is not a number
    
    Examples:
        >>> add_numbers(2, 3)
        5
        >>> add_numbers(2.5, 3.7)
        6.2
        >>> add_numbers(-1, 5)
        4
    """
    # Type checking to ensure inputs are numbers
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers (int or float)")
    
    return a + b