from typing import Union, List, Tuple
from collections import Counter

# Tantrix helper functions

tiles_complete = ['112323', '212313', '131322', '112332', '131223', '121332', '113232',
                  '112233', '121323', '113223', '131232', '221331', '113322', '121233',
                  '232344', '242343', '224343', '332442', '223434', '242433', '232443',
                  '223344', '323424', '223443', '232434', '224334', '224433', '242334',
                  '114343', '313414', '131344', '114334', '131443', '141334', '113434',
                  '114433', '141343', '113443', '131434', '331441', '113344', '141433',
                  '112424', '212414', '141422', '112442', '141224', '121442', '114242',
                  '112244', '121424', '114224', '141242', '221441', '114422', '121244']


def get_dist(tile, col):
    """
    Distance between the two occurrences of a color in a tile encoding.
    Example: get_dist("121323", 1) returns 2 (distance) and starting index.
    :param tile: encoding string of a tile
    :param col: color to search for (as int or value convertible to str)
    :return: (distance between the two color positions, index of first occurrence)
    """
    if str(col) not in tile:
        return 0, 0
    indices = []
    for r in range(6):
        if tile[r] == str(col):
            indices.append(r)
    dist = indices[1] - indices[0]
    return dist, indices[0]


def shift_tile(tile, offset: int):
    """
    Shift a tile encoding circularly by offset positions to the left.
    :param tile: a list (or sequence) with the six color values of the tile
    :param offset: how many positions to shift (positive = shift left)
    :return: shifted tile as a new list
    """
    return [tile[(i + offset) % 6] for i in range(6)]


def sort_sol(tile):
    """
    Rotate the tile encoding into a canonical orientation.
    The function searches for a color j in {1,2,3} whose two occurrences
    determine the proper rotation and then rotates the tile accordingly.

    :param tile: tile encoding (iterable of length 6)
    :return: rotated tile (list) in canonical position
    """
    for j in range(1, 4):
        distance, index = get_dist(tile, j)
        if distance in [1, 2, 4, 5]:
            if distance < 4:
                tile = shift_tile(tile, index)
            else:
                tile = shift_tile(tile, index + distance)
            break
    return tile


# Matching functions


def preprocess_input(raw_input: List[Union[int, List[int]]]) -> List[List[int]]:
    """
    Generate all plausible variants from the raw input by expanding choices (lists),
    removing zeros and then compressing consecutive duplicates.

    Example input: [3, [4, 3], 3, 1, 0, [4, 1], 1, [4, 3]]
    The expansion logic keeps different orderings for ambiguous slots and creates
    a set of compressed candidate sequences (as strings).

    :param raw_input: list of ints or lists representing ambiguous entries
    :return: a list of candidate strings representing compressed variants
    """
    # Remove all zero entries
    cleaned = [entry for entry in raw_input if entry != 0]

    # Expand entries: for each entry, either append the single value or
    # expand choice-lists into multiple branches. The original expansion logic
    # from the project is preserved.
    expanded = [[]]
    for entry in cleaned:
        if isinstance(entry, list):
            expanded_list_length = len(expanded)
            for i in range(expanded_list_length):
                exp = expanded[i]
                # keep permutations and variants similar to the original behavior
                expanded.append(exp + [entry[1], entry[0]])
                expanded.append(exp + [entry[0]])
                expanded.append(exp + [entry[1]])
                exp += entry
        else:
            for exp in expanded:
                exp.append(entry)

    # Remove consecutive duplicate values in each variant and ensure circular
    # duplicates (last == first) are eliminated.
    def compress(seq: List[int]) -> List[int]:
        compressed = [seq[0]]
        for x in seq[1:]:
            if x != compressed[-1]:
                compressed.append(x)
        if compressed[-1] == compressed[0]:  # Remove last element if equal to first
            compressed = compressed[:-1]
        return compressed

    compressed_variants = {tuple(compress(list(variant))) for variant in expanded}
    # keep only variants shorter than full tile length
    compressed_variants = {var for var in compressed_variants if len(var) < 7}
    selected_variants = []
    for variant in compressed_variants:
        c = Counter(variant)
        # discard variants where any color appears 3 or more times
        if max(c.values()) < 3:
            selected_variants.append(''.join([str(pos) for pos in variant]))
    return selected_variants
                


def match_pattern(compressed_input: str, pattern: str) -> Union[str, None]:
    """
    Attempt to find a unique assignment of variables in `pattern` to the
    digits in `compressed_input`. If successful, return the expanded tile code
    string (e.g. '223131' for pattern 'aabcbc'). Otherwise return None.

    :param compressed_input: compressed candidate string (e.g. '23131')
    :param pattern: compact pattern using letters like 'abcbc', 'abc' etc.
    :return: expanded tile code string or None
    """
    if len(compressed_input) != len(pattern):
        return None

    mapping = {}
    used_values = {}

    for char_pat, char_inp in zip(pattern, compressed_input):
        if char_pat in mapping:
            if mapping[char_pat] != char_inp:
                return None  # contradiction
        else:
            if char_inp in used_values:
                return None  # two pattern letters map to the same digit
            mapping[char_pat] = char_inp
            used_values[char_inp] = True
    # Debug prints preserved from original
    print(f"{mapping=}")
    print(f"{used_values=}")
    # Reconstruct the full expanded type string (e.g. 'aabcbc' -> '223131')
    full_type_expanded = ''.join(mapping[c] for c in expand_pattern(pattern))
    return full_type_expanded


def expand_pattern(pattern: str) -> str:
    """
    Return the expanded version of a compact pattern.
    Examples:
        'abc'    -> 'aabbcc'   (type ccc)
        'abcbc'  -> 'aabcbc'   (type cxx)
        'abcb'   -> 'aabccb'   (type clc)
        'abacbc' -> 'abacbc'   (type clh)
    """
    expansions = {
        'abc':    'aabbcc',     # ccc
        'abcbc':  'aabcbc',     # cxx
        'abcb':   'aabccb',     # clc
        'abacbc': 'abacbc',     # clh
    }
    return expansions.get(pattern, pattern)  # Fallback: no expansion


def rotate_string(s: str, n: int) -> str:
    return s[n:] + s[:n]


def find_matching_type(compressed_input: str, input_pattern: str = None) -> Union[Tuple['str', 'str'], None]:
    """
    Try to match a compressed input string against known tile patterns.
    If an explicit input_pattern is provided, only that pattern is tried.
    Otherwise a default set of patterns is attempted.

    The function rotates the input string to account for circular shifts.
    Returns the matched expanded tile string or None.
    """
    if input_pattern is None:
        known_patterns = ['abc', 'abcbc', 'abcb', 'ababcb']  # can be adapted
    else:
        known_patterns = [input_pattern]

    for pattern in known_patterns:
        print(f"{pattern=}")
        for shift in range(len(compressed_input)):
            rotated = rotate_string(compressed_input, shift)
            print(f"{rotated=}")
            match = match_pattern(rotated, pattern)
            if match:
                return match
    return None


def check_variants(input_variants: List[List[int]], input_pattern: str = None) -> Union[str, None]:
    """
    Check a list of candidate variants (strings) and return the first
    variant that matches a known tile pattern (optionally restricted to
    `input_pattern`). Returns the matched expanded string or None.
    """
    for variant in input_variants:
        output = find_matching_type(variant, input_pattern=input_pattern)
        if output is not None:
            return output
    return None


def get_tile_number(matched_variant: Union[str, None]) -> Union[int, None]:
    """
    Return the index (tile number) of the matched variant within the
    master list `tiles_complete`. The matched_variant is first
    standardized (rotated) using `sort_sol` and then looked up.
    Returns None if matched_variant is None.
    """
    if matched_variant is not None:
        standardized_format = ''.join(sort_sol(matched_variant))
        tile_number = tiles_complete.index(standardized_format)
        print(f"{tile_number=}")
        return tile_number
    return None


def main():
    variants = preprocess_input([3, [4, 3], 3, 1, 0, [4, 1], 1, [4, 3]])
    print(f"{variants=}")
    out = check_variants(variants, input_pattern='abacbc')
    print(f"{out=}")
    get_tile_number(out)
    
if __name__ == "__main__":
    main()
