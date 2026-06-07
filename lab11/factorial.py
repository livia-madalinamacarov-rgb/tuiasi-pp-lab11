"""
Calcul factorial paralel folosind multiprocessing.

Tema 1: calculează n! simultan pentru mai multe valori,
folosind atât multiprocessing.Queue + Process cât și ProcessPoolExecutor.
"""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor


def factorial(n: int) -> int:
    """Calculează n! (factorial).

    Args:
        n: Numărul pentru care se calculează factorialul. Trebuie să fie >= 0.

    Returns:
        n! ca întreg.

    Raises:
        ValueError: Dacă n este negativ.
    """
    if n < 0:
        raise ValueError("Numărul trebuie să fie mai mare sau egal cu 0.")

    rezultat = 1
    for i in range(1, n + 1):
        rezultat *= i
    return resultado if n > 0 else 1


def _worker_factorial(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue) -> None:
    """Funcție worker pentru procesul multiprocessing.

    Citește valori din input_queue, calculează factorialul și trimite
    rezultatele în output_queue sub forma (n, factorial(n)).

    Se oprește când primește None din input_queue.
    """
    while True:
        n = input_queue.get()
        if n is None:
            break
        try:
            rez = factorial(n)
            output_queue.put((n, rez))
        except Exception as e:
            # În caz de eroare neprevăzută, putem trimite excepția sau ignora
            pass


def parallel_factorial_multiprocessing(values: list[int]) -> dict[int, int]:
    """Calculează factorialul pentru mai multe valori în paralel.

    Folosește 4 procese worker cu multiprocessing.Queue și multiprocessing.Process.
    """
    if not values:
        return {}

    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()

    # Punem toate valorile în coada de intrare
    for v in values:
        input_queue.put(v)

    # Numărul de procese cerut este 4
    num_workers = 4
    procese = []

    # Pornim procesele worker
    for _ in range(num_workers):
        p = multiprocessing.Process(target=_worker_factorial, args=(input_queue, output_queue))
        p.start()
        procese.append(p)
        # Trimitem semnalul de oprire (None) pentru fiecare worker în coadă
        input_queue.put(None)

    rezultate = {}
    # Colectăm exact atâtea rezultate câte valori am trimis inițial
    for _ in range(len(values)):
        n, rez = output_queue.get()
        rezultate[n] = rez

    # Așteptăm ca toate procesele să își termine execuția în siguranță
    for p in procese:
        p.join()

    return rezultate


def parallel_factorial_futures(values: list[int]) -> dict[int, int]:
    """Calculează factorialul pentru mai multe valori în paralel.

    Folosește concurrent.futures.ProcessPoolExecutor cu max_workers=4.
    """
    if not values:
        return {}

    rezultate = {}
    with ProcessPoolExecutor(max_workers=4) as executor:
        # map menține asocierea dintre input și funcție
        dict_rezultate = executor.map(factorial, values)

        for n, rez in zip(values, dict_rezultate):
            rezultate[n] = rez

    return rezultate