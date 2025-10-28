import re

def strcmp_substitution(s1, s2, **kwargs):
    """
    Checks strings for match with ability to substitute a symbol for a string.
    """
    substitute_string_symbol = kwargs.get('SubstituteStringSymbol', '#')
    use_substitute_string = kwargs.get('UseSubstituteString', True)
    substitute_string = kwargs.get('SubstituteString', '')

    if isinstance(s2, str):
        s2 = [s2]

    tf = [False] * len(s2)
    match_string = [''] * len(s2)
    substitute_string_out = [''] * len(s2)

    for i, s in enumerate(s2):
        if use_substitute_string and substitute_string_symbol in s1:
            if substitute_string:
                s1_re = s1.replace(substitute_string_symbol, re.escape(substitute_string))
                if re.fullmatch(s1_re, s):
                    tf[i] = True
                    match_string[i] = s
                    substitute_string_out[i] = substitute_string
            else:
                s1_re = s1.replace(substitute_string_symbol, '(.+)')
                match = re.fullmatch(s1_re, s)
                if match:
                    tf[i] = True
                    match_string[i] = s
                    substitute_string_out[i] = match.group(1)
        else:
            if re.fullmatch(s1, s):
                tf[i] = True
                match_string[i] = s

    return tf, match_string, substitute_string_out

def str2intseq(s, **kwargs):
    """
    Recover a sequence of integers from a string.
    """
    sep = kwargs.get('sep', ',')
    seq = kwargs.get('seq', '-')

    a = []
    parts = s.split(sep)
    for part in parts:
        part = part.strip()
        if seq in part:
            start, end = map(int, part.split(seq))
            a.extend(range(start, end + 1))
        else:
            a.append(int(part))
    return a

def intseq2str(a, **kwargs):
    """
    Convert an array of integers to a compact string, maintaining sequence.
    """
    sep = kwargs.get('sep', ',')
    seq = kwargs.get('seq', '-')

    if not a:
        return ""

    a = sorted(a)
    s = []
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[j + 1] == a[j] + 1:
            j += 1

        if j > i + 1:
            s.append(f"{a[i]}{seq}{a[j]}")
        else:
            s.append(str(a[i]))
            if j == i + 1:
                 s.append(str(a[j]))

        i = j + 1

    return sep.join(s)
