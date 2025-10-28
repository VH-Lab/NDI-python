import re

def name_to_variable_name(name):
    """
    Converts a string into a camelCase variable name format.
    """
    if not isinstance(name, str):
        raise TypeError("Input must be a string.")

    if not name or name.isspace():
        return ""

    # Replace specific characters with spaces
    name = name.replace(':', ' ').replace('-', ' ')

    # Replace non-alphanumeric characters (except underscore) with spaces
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', ' ', name)

    # Split into words and build camelCase
    words = re.split(r'[\s_]+', cleaned_name)
    if not words:
        return ""

    words = [word for word in words if word]
    if not words:
        return ""

    first_word = words[0].lower()
    capitalized_words = [word.capitalize() for word in words[1:]]

    # Join words and ensure it starts with a letter
    variable_name = first_word + "".join(capitalized_words)
    if not variable_name:
        return ""

    if not variable_name[0].isalpha():
        variable_name = "var_" + variable_name

    # Final cleanup
    variable_name = re.sub(r'[^a-zA-Z0-9_]', '', variable_name)

    return variable_name
