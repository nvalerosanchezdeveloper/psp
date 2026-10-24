"""P1.1 · Suma de cuadrados por procesos.

Procesador de lotes que calcula la suma de los cuadrados de una lista de
enteros no negativos, en una versión secuencial y otra que reparte los lotes
entre procesos con ProcessPoolExecutor y un contexto spawn explícito.

Formatos del contrato:
    Lote      -> (id_lote, numeros)
    Resultado -> (id_lote, pid, cantidad, suma_parcial)
"""

import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor


# ---------------------------------------------------------------------------
# Funciones auxiliares de validación
# ---------------------------------------------------------------------------

def _validar_config(valor, nombre):
    """Lanza ValueError si `valor` no es un entero positivo no booleano.

    bool se comprueba primero porque en Python es subclase de int
    (isinstance(True, int) es True y True == 1).
    """
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError(f"{nombre} debe ser un entero positivo, no {valor!r}")


def _es_dato_valido(x):
    """Un dato es válido si es un entero >= 0 y no es booleano."""
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


# ---------------------------------------------------------------------------
# Funciones del ejercicio
# ---------------------------------------------------------------------------

def crear_lotes(datos, tamano_lote):
    """Divide `datos` en lotes (id_lote, numeros) con IDs consecutivos desde 0.

    Cada dato aparece en un único lote; el último puede quedar incompleto.
    La configuración se valida antes de recorrer los datos, de modo que el
    ValueError se produce también con una lista vacía.
    """
    _validar_config(tamano_lote, "tamano_lote")
    lotes = []
    for id_lote, inicio in enumerate(range(0, len(datos), tamano_lote)):
        lotes.append((id_lote, list(datos[inicio:inicio + tamano_lote])))
    return lotes


def calcular_lote(lote):
    """Función trabajadora: procesa un lote y devuelve su resultado identificado.

    Está definida en el nivel del módulo para que los procesos creados con
    spawn puedan importarla y localizarla por su nombre.

    El PID se obtiene aquí dentro para registrar el proceso que realmente
    ejecuta el lote. El trabajador no modifica ninguna variable del
    coordinador: cada proceso tiene su propio espacio de direcciones, así que
    la única vía de comunicación es devolver el resultado.
    """
    id_lote, numeros = lote
    pid = os.getpid()
    suma = 0
    for x in numeros:
        if not _es_dato_valido(x):
            raise ValueError(f"Lote {id_lote} (PID {pid}): dato inválido {x!r}")
        suma += x * x
    return (id_lote, pid, len(numeros), suma)


def agregar_resultados(lotes, resultados):
    """Valida los resultados frente a los lotes planificados y devuelve el total.

    Comprueba que cada ID esperado aparece exactamente una vez, que no hay IDs
    desconocidos, que la cantidad de cada lote coincide con la planificada y
    que el total de elementos es correcto. Trabaja por ID (diccionario), no
    por posición, por lo que no depende del orden de los resultados.

    El total final se calcula aquí, en el coordinador, y solo después de que
    todas las comprobaciones hayan pasado.
    """
    esperado = {id_lote: len(numeros) for id_lote, numeros in lotes}
    parciales = {}

    for r in resultados:
        if len(r) != 4 or any(isinstance(c, bool) or not isinstance(c, int) for c in r):
            raise ValueError(f"Resultado mal formado: {r!r}")
        id_lote, _pid, cantidad, suma = r

        if id_lote not in esperado:
            raise ValueError(f"ID de lote desconocido: {id_lote}")
        if id_lote in parciales:
            raise ValueError(f"Resultado duplicado para el lote {id_lote}")
        if cantidad != esperado[id_lote]:
            raise ValueError(
                f"Lote {id_lote}: cantidad {cantidad}, se esperaban {esperado[id_lote]}"
            )
        parciales[id_lote] = suma

    faltan = set(esperado) - set(parciales)
    if faltan:
        raise ValueError(f"Faltan resultados de los lotes: {sorted(faltan)}")

    if sum(r[2] for r in resultados) != sum(esperado.values()):
        raise ValueError("El total de elementos procesados no coincide con el planificado")

    return sum(parciales.values())


def ejecutar_secuencial(datos, tamano_lote):
    """Ejecuta calcular_lote para todos los lotes en el propio coordinador.

    Devuelve (total, resultados).
    """
    lotes = crear_lotes(datos, tamano_lote)
    resultados = [calcular_lote(lote) for lote in lotes]
    return agregar_resultados(lotes, resultados), resultados


def ejecutar_procesos(datos, tamano_lote, max_workers):
    """Reparte los lotes entre procesos trabajadores.

    - Contexto spawn explícito: cada trabajador arranca un intérprete nuevo
      que importa este módulo (mismo comportamiento en Windows y Linux).
    - Un único ProcessPoolExecutor por ejecución.
    - El bloque with llama a shutdown(wait=True) al salir: espera y cierra
      los trabajadores también cuando una tarea ha fallado.
    - list(...) consume el iterador de map, de forma que los resultados y las
      excepciones de los trabajadores se hacen visibles en el coordinador.

    Devuelve (total, resultados).
    """
    _validar_config(max_workers, "max_workers")
    lotes = crear_lotes(datos, tamano_lote)
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=max_workers, mp_context=ctx) as pool:
        resultados = list(pool.map(calcular_lote, lotes))
    return agregar_resultados(lotes, resultados), resultados
