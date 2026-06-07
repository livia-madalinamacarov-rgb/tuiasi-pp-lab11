"""
Pipeline de procesare paralelă a fișierelor.

Tema 2: procesează mai multe fișiere simultan în 3 etape:
1. Citire conținut
2. Numărare cuvinte
3. Scriere rezultat
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def read_file(path: str) -> str:
    """Citește conținutul unui fișier text."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fișierul {path} nu există.")

    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def count_words(text: str) -> dict[str, int]:
    """Numără frecvența fiecărui cuvânt din text.

    Cuvintele sunt separate prin spații și/sau newline-uri.
    Comparația este case-sensitive.
    """
    if not text:
        return {}

    # split() fără argumente separă automat după orice spațiu alb (spații, taburi, newline)
    cuvinte = text.split()

    frecvente = {}
    for cuvint in cuvinte:
        frecvente[cuvint] = frecvente.get(cuvint, 0) + 1

    return frecvente


def write_result(result: dict, output_path: str) -> None:
    """Scrie rezultatul numărării cuvintelor în fișier JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)


def _process_single_file(args: tuple[str, str]) -> None:
    """Procesează un singur fișier prin cele 3 etape.

    Args:
        args: Tuplu (input_path, output_path).
    """
    input_path, output_path = args

    # 1. Citește conținutul
    continut = read_file(input_path)

    # 2. Numără cuvintele
    rezultat_numarare = count_words(continut)

    # 3. Scrie rezultatul
    write_result(rezultat_numarare, output_path)


def process_files_pipeline(input_paths: list[str], output_dir: str) -> None:
    """Procesează mai multe fișiere în paralel folosind un pipeline cu ThreadPoolExecutor.

    Fișierele sunt procesate simultan (nu secvențial).
    """
    if not input_paths:
        return

    # Pregătim tuplurile de argumente (input, output) pentru fiecare fișier în parte
    liste_argumente = []
    p_output_dir = Path(output_dir)

    for calea_in in input_paths:
        p_in = Path(calea_in)
        # Înlocuim extensia cu .json și construim noua cale în directorul de destinație
        calea_out = str(p_output_dir / p_in.with_suffix('.json').name)
        liste_argumente.append((calea_in, calea_out))

    # Executăm procesarea fișierelor în paralel în pool-ul de fire de execuție
    with ThreadPoolExecutor() as executor:
        executor.map(_process_single_file, liste_argumente)