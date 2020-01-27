"""Utilities"""
import re


# Captures "words" in pascal case
pascal_pattern = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
def pascal_to_snake_case(string):
  """Converts  PascalCase strings to snake_case
  
  :param string: String without whitespace.
  :type string: str
  :return: String in snake case.
  :rtype: str
  """
  return pascal_pattern.sub(r'_\1', string).lower()