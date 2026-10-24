"""Lanzador de la P1.1: ejecuta y mide las variantes secuencial y con procesos.

Ejemplos:
    python ejecutar.py --lote 7 --workers 2 --repeticiones 5 --detalle
    python ejecutar.py --modo procesos --datos "[1,-1,3]" --lote 2 --repeticiones 1
"""

import argparse
import json
import statistics
import sys
import time

from suma_cuadrados import ejecutar_procesos, ejecutar_secuencial

REFERENCIA = 42925
DATOS_REFERENCIA = list(range(1, 51))


def leer_argumentos():
    p = argparse.ArgumentParser(description="Suma de cuadrados por lotes")
    p.add_argument("--modo", choices=["ambos", "secuencial", "procesos"], default="ambos")
    p.add_argument("--datos", help='Lista JSON de enteros, p. ej. "[1,2,3]". Por defecto 1..50')
    p.add_argument("--lote", type=int, default=7, help="Tamaño de lote")
    p.add_argument("--workers", type=int, default=2, help="Máximo de procesos trabajadores")
    p.add_argument("--repeticiones", type=int, default=5)
    p.add_argument("--detalle", action="store_true", help="Muestra cada resultado de lote")
    return p.parse_args()


def medir(variante, datos, lote, workers):
    """Mide particionado, cálculo y agregación (y, en procesos, creación,
    uso y cierre del pool). La impresión queda fuera del intervalo medido."""
    inicio = time.perf_counter()
    if variante == "secuencial":
        total, resultados = ejecutar_secuencial(datos, lote)
    else:
        total, resultados = ejecutar_procesos(datos, lote, workers)
    duracion = time.perf_counter() - inicio
    return total, resultados, duracion


def main():
    args = leer_argumentos()
    datos = DATOS_REFERENCIA if args.datos is None else json.loads(args.datos)
    if not isinstance(datos, list):
        raise ValueError("--datos debe ser una lista JSON")
    if args.repeticiones < 1:
        raise ValueError("--repeticiones debe ser al menos 1")

    variantes = ["secuencial", "procesos"] if args.modo == "ambos" else [args.modo]
    tiempos = {v: [] for v in variantes}
    totales = {}

    for rep in range(args.repeticiones):
        # Se alterna el orden para que ninguna variante salga beneficiada
        # sistemáticamente por ejecutarse primero o segunda.
        orden = variantes if rep % 2 == 0 else list(reversed(variantes))
        for variante in orden:
            total, resultados, duracion = medir(variante, datos, args.lote, args.workers)
            tiempos[variante].append(duracion)
            totales[variante] = total
            print(f"[rep {rep + 1}] {variante:<10} total={total}  "
                  f"lotes={len(resultados)}  tiempo={duracion * 1000:.3f} ms")
            if args.detalle:
                for id_lote, pid, cantidad, suma in resultados:
                    print(f"      lote {id_lote}: pid={pid} cantidad={cantidad} suma={suma}")

    if len(set(totales.values())) > 1:
        raise RuntimeError(f"Las variantes no coinciden: {totales}")
    if datos == DATOS_REFERENCIA and any(t != REFERENCIA for t in totales.values()):
        raise RuntimeError(f"El total no coincide con la referencia {REFERENCIA}")

    print("\nResumen (ms):")
    medianas = {}
    for v in variantes:
        medianas[v] = statistics.median(tiempos[v])
        lista = ", ".join(f"{t * 1000:.3f}" for t in tiempos[v])
        print(f"  {v:<10} tiempos=[{lista}]  mediana={medianas[v] * 1000:.3f}")
    if len(variantes) == 2:
        aceleracion = medianas["secuencial"] / medianas["procesos"]
        print(f"  aceleración = mediana secuencial / mediana procesos = {aceleracion:.4f}")


if __name__ == "__main__":
    # Imprescindible con spawn: cada trabajador importa el módulo principal y,
    # sin esta protección, volvería a ejecutar main() y a crear procesos.
    try:
        main()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
