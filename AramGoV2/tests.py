"""
Tests for AramGoV2 utility functions.
"""

from django.test import TestCase
from AramGoV2.util.math_utils import add_numbers


class MathUtilsTest(TestCase):
    """Test cases for mathematical utility functions."""
    
    def test_add_positive_integers(self):
        """Test adding two positive integers."""
        result = add_numbers(2, 3)
        self.assertEqual(result, 5)
    
    def test_add_negative_integers(self):
        """Test adding two negative integers."""
        result = add_numbers(-2, -3)
        self.assertEqual(result, -5)
    
    def test_add_positive_and_negative_integers(self):
        """Test adding a positive and negative integer."""
        result = add_numbers(5, -3)
        self.assertEqual(result, 2)
    
    def test_add_with_zero(self):
        """Test adding with zero."""
        result = add_numbers(5, 0)
        self.assertEqual(result, 5)
        
        result = add_numbers(0, 7)
        self.assertEqual(result, 7)
        
        result = add_numbers(0, 0)
        self.assertEqual(result, 0)
    
    def test_add_floats(self):
        """Test adding floating point numbers."""
        result = add_numbers(2.5, 3.7)
        self.assertAlmostEqual(result, 6.2, places=1)
    
    def test_add_integer_and_float(self):
        """Test adding an integer and a float."""
        result = add_numbers(2, 3.5)
        self.assertAlmostEqual(result, 5.5, places=1)
        
        result = add_numbers(3.5, 2)
        self.assertAlmostEqual(result, 5.5, places=1)
    
    def test_add_large_numbers(self):
        """Test adding large numbers."""
        result = add_numbers(1000000, 2000000)
        self.assertEqual(result, 3000000)
    
    def test_add_very_small_numbers(self):
        """Test adding very small floating point numbers."""
        result = add_numbers(0.0001, 0.0002)
        self.assertAlmostEqual(result, 0.0003, places=4)
    
    def test_add_numbers_type_error_string(self):
        """Test that TypeError is raised when passing strings."""
        with self.assertRaises(TypeError):
            add_numbers("2", 3)
        
        with self.assertRaises(TypeError):
            add_numbers(2, "3")
        
        with self.assertRaises(TypeError):
            add_numbers("2", "3")
    
    def test_add_numbers_type_error_none(self):
        """Test that TypeError is raised when passing None."""
        with self.assertRaises(TypeError):
            add_numbers(None, 3)
        
        with self.assertRaises(TypeError):
            add_numbers(2, None)
    
    def test_add_numbers_type_error_list(self):
        """Test that TypeError is raised when passing lists."""
        with self.assertRaises(TypeError):
            add_numbers([1, 2], 3)
        
        with self.assertRaises(TypeError):
            add_numbers(2, [3, 4])
    
    def test_add_numbers_type_error_dict(self):
        """Test that TypeError is raised when passing dictionaries."""
        with self.assertRaises(TypeError):
            add_numbers({"a": 1}, 3)
        
        with self.assertRaises(TypeError):
            add_numbers(2, {"b": 3})