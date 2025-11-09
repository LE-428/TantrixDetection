from typing import Union, List, Tuple
from collections import Counter

# Tantrix functions

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
    Abstand von einer Farbe in der Codierung, Beispiel: get_dist("121323", 1) liefert 2
    :param tile: Codierung eines Steins
    :param col: gesuchte Farbe
    :return: Abstand im array zwischen den beiden farbigen Kanten
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
    :param tile: eine Liste mit den Farben des Spielsteins
    :param offset: um wie viele Stellen wird die Codierung von rechts nach links verschoben
    :return: das verschobene Tile
    """
    return [tile[(i + offset) % 6] for i in range(6)]


def sort_sol(tile):
    """
    Stein-codierung richtig verschieben
    :param tile: Codierung eines Steins
    :return: korrekte Codierung
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
    Erzeugt alle möglichen Varianten des Inputs, indem Wahlmöglichkeiten (Listen) aufgelöst werden,
    Nullen entfernt und dann Duplikate in Folge entfernt werden.
    Beispiel: [3, [4, 3], 3, 1, 0, [4, 1], 1, [4, 3]]
    """
    # Entferne alle 0-Werte
    cleaned = [entry for entry in raw_input if entry != 0]

    # Für jeden Eintrag entweder die Zahl als Liste oder direkt übernehmen
    expanded = [[]]
    for entry in cleaned:
        # print(f"{entry=}")
        if isinstance(entry, list):
            expanded_list_length = len(expanded)
            for i in range(expanded_list_length):
                exp = expanded[i]
                expanded.append(exp + [entry[1], entry[0]])
                expanded.append(exp + [entry[0]])
                expanded.append(exp + [entry[1]])
                exp += entry
        else:
            # print(f"int")
            for exp in expanded:
                exp.append(entry)
    # print(f"{expanded=}")

    # Entferne direkt aufeinanderfolgende Duplikate in jeder Variante
    def compress(seq: List[int]) -> List[int]:
        compressed = [seq[0]]
        for x in seq[1:]:
            if x != compressed[-1]:
                compressed.append(x)
        if compressed[-1] == compressed[0]:  # Entferne das letzte Element, falls es dem ersten gleicht
            compressed = compressed[:-1]
        return compressed

    compressed_variants = {tuple(compress(list(variant))) for variant in expanded}
    compressed_variants = {var for var in compressed_variants if len(var) < 7}
    selected_variants = []
    for variant in compressed_variants:
        c = Counter(variant)
        if max(c.values()) < 3:
            selected_variants.append(''.join([str(pos) for pos in variant]))
    return selected_variants
        


def match_pattern(compressed_input: str, pattern: str) -> Union[str, None]:
    """
    Versucht, eine eindeutige Variablenbelegung für pattern -> compressed_input zu finden.
    Gibt die ausgeschriebene Typenfolge zurück, z.B. '223131' für 'aabcbc', wenn möglich.
    Sonst None.
    """
    if len(compressed_input) != len(pattern):
        return None

    mapping = {}
    used_values = {}

    for char_pat, char_inp in zip(pattern, compressed_input):
        if char_pat in mapping:
            if mapping[char_pat] != char_inp:
                return None  # Widerspruch
        else:
            if char_inp in used_values:
                return None  # Zwei Buchstaben sollen auf gleiche Farbe gehen
            mapping[char_pat] = char_inp
            used_values[char_inp] = True
    print(f"{mapping=}")
    print(f"{used_values=}")
    # Rekonstruiere die vollständige Typenfolge (z. B. 'aabcbc' -> '223131')
    full_type_expanded = ''.join(mapping[c] for c in expand_pattern(pattern))
    return full_type_expanded


def expand_pattern(pattern: str) -> str:
    """
    Gibt die erweiterte Version eines komprimierten Musters zurück.
    Beispiele:
        'abc'    -> 'aabbcc'   (Typ ccc)
        'abcbc'  -> 'aabcbc'   (Typ cxx)
        'abcb'   -> 'aabccb'    (Typ clc)
        'abacbc' -> 'abacbc' (Typ clh)
    """
    # Beispielhafte Regeln (müssen evtl. je nach Konvention angepasst werden)
    expansions = {
        'abc':    'aabbcc',     # ccc
        'abcbc':  'aabcbc',     # cxx
        'abcb':   'aabccb',      # clc
        'abacbc': 'abacbc',   # clh
    }
    return expansions.get(pattern, pattern)  # Fallback: keine Expansion


def rotate_string(s: str, n: int) -> str:
    return s[n:] + s[:n]


def find_matching_type(compressed_input: str, input_pattern: str = None) -> Union[Tuple['str', 'str'], None]:
    if input_pattern is None:
        known_patterns = ['abc', 'abcbc', 'abcb', 'ababcb']  # kann angepasst werden
    else:
        known_patterns = [input_pattern]

    for pattern in known_patterns:
        print(f"{pattern=}")
        for shift in range(len(compressed_input)):
            # print(f"{shift=}")
            rotated = rotate_string(compressed_input, shift)
            print(f"{rotated=}")
            match = match_pattern(rotated, pattern)
            if match:
                # return pattern, match
                return match
    return None


def check_variants(input_variants: List[List[int]], input_pattern: str = None) -> Union[str, None]:
    for variant in input_variants:
        output = find_matching_type(variant, input_pattern=input_pattern)
        if output is not None:
            return output
    return None


def get_tile_number(matched_variant: Union[str, None]) -> Union[int, None]:
    """Get the index of the Tantrix tile"""
    if matched_variant is not None:
        standardized_format = ''.join(sort_sol(matched_variant))
        tile_number = tiles_complete.index(standardized_format)
        print(f"{tile_number=}")
        return tile_number
    return None


def main():
    variants = preprocess_input([3, [4, 3], 3, 1, 0, [4, 1], 1, [4, 3]])
    print(f"{variants=}")
    # out = find_matching_type('23131', input_pattern=None)
    out = check_variants(variants, input_pattern='abacbc')
    print(f"{out=}")
    get_tile_number(out)
    
if __name__ == "__main__":
    main()
