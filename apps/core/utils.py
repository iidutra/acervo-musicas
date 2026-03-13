"""Utilitários de normalização de tom musical."""

# Mapping of Portuguese tone names to standard notation
TONE_MAP = {
    # Maiores
    'dó': 'C', 'do': 'C', 'ré': 'D', 're': 'D',
    'mi': 'E', 'fá': 'F', 'fa': 'F',
    'sol': 'G', 'lá': 'A', 'la': 'A', 'si': 'B',
    # Direct mappings
    'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F',
    'g': 'G', 'a': 'A', 'b': 'B',
}

MODIFIER_MAP = {
    'sustenido': '#', 'sharp': '#', '#': '#',
    'bemol': 'b', 'flat': 'b', 'b': 'b',
}

VALID_TONES = {
    'C', 'Cm', 'C#', 'C#m', 'Db', 'Dbm',
    'D', 'Dm', 'D#', 'D#m', 'Eb', 'Ebm',
    'E', 'Em',
    'F', 'Fm', 'F#', 'F#m', 'Gb', 'Gbm',
    'G', 'Gm', 'G#', 'G#m', 'Ab', 'Abm',
    'A', 'Am', 'A#', 'A#m', 'Bb', 'Bbm',
    'B', 'Bm',
}

# Enharmonic normalization (prefer flats for common keys)
ENHARMONIC = {
    'Db': 'C#', 'Dbm': 'C#m',
    'Gb': 'F#', 'Gbm': 'F#m',
    'A#': 'Bb', 'A#m': 'Bbm',
    'D#': 'Eb',  # Keep D#m as is since it's used
}


def normalizar_tom(tom_raw: str) -> str | None:
    """
    Normaliza um tom musical para notação padrão.

    Returns the normalized tone string or None if unrecognizable.

    Examples:
        'Dó' -> 'C'
        'Lá menor' -> 'Am'
        'Si bemol' -> 'Bb'
        'Fá sustenido menor' -> 'F#m'
        'C#' -> 'C#'
        'Am' -> 'Am'
        '' -> None
    """
    if not tom_raw or not tom_raw.strip():
        return None

    raw = tom_raw.strip().lower()

    # If it's already a valid tone (case-adjusted)
    # Try direct match first
    for valid in VALID_TONES:
        if raw == valid.lower():
            return ENHARMONIC.get(valid, valid)

    # Parse Portuguese format
    parts = raw.replace('-', ' ').split()
    if not parts:
        return None

    # Get base note
    base = TONE_MAP.get(parts[0])
    if not base:
        return None

    modifier = ''
    is_minor = False

    for part in parts[1:]:
        if part in ('menor', 'minor', 'm'):
            is_minor = True
        elif part in MODIFIER_MAP:
            modifier = MODIFIER_MAP[part]
        elif part == 'maior' or part == 'major':
            pass  # major is default

    result = f"{base}{modifier}{'m' if is_minor else ''}"

    if result in VALID_TONES:
        return ENHARMONIC.get(result, result)

    return None
