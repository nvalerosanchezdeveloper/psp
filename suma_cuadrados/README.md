# P1.1 · Suma de cuadrados por procesos

Procesador de lotes que calcula 1² + 2² + … + 50² = **42925** de dos formas: secuencial y repartiendo los lotes entre procesos con `ProcessPoolExecutor` y un contexto `spawn` explícito.

## Requisitos

- Python 3.14.x
- Sin bibliotecas externas

## Preparación del entorno

**Windows (PowerShell):**
```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.version); print(sys.executable)"
```

**Linux:**
```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -c "import sys; print(sys.version); print(sys.executable)"
```

La ruta impresa debe estar dentro de `.venv`. Sin activar el entorno, usa la ruta explícita: `.venv\Scripts\python.exe` (Windows) o `.venv/bin/python` (Linux).

## Uso

Ejecutar siempre desde la terminal, dentro de esta carpeta (no en consola interactiva ni en cuadernos).

| Qué | Comando |
|---|---|
| Pruebas P01–P13 | `python pruebas.py` |
| Caso normal | `python ejecutar.py --lote 7 --workers 2 --repeticiones 1 --detalle` |
| Medición (5 repeticiones) | `python ejecutar.py --lote 7 --workers 2 --repeticiones 5 --detalle` |
| Fallo controlado | `python ejecutar.py --modo procesos --datos "[1,-1,3]" --lote 2 --repeticiones 1` |

Código de salida tras el fallo controlado: `$LASTEXITCODE` (PowerShell) o `echo $?` (Linux). Debe ser distinto de 0.

### Opciones de `ejecutar.py`

| Opción | Por defecto | Descripción |
|---|---|---|
| `--modo` | `ambos` | `ambos`, `secuencial` o `procesos` |
| `--datos` | 1..50 | Lista JSON de enteros |
| `--lote` | 7 | Tamaño de lote |
| `--workers` | 2 | Máximo de procesos trabajadores |
| `--repeticiones` | 5 | Mediciones por variante |
| `--detalle` | — | Muestra lote, PID, cantidad y suma de cada resultado |

## Archivos

| Archivo | Contenido |
|---|---|
| `suma_cuadrados.py` | `crear_lotes`, `calcular_lote`, `agregar_resultados`, `ejecutar_secuencial`, `ejecutar_procesos` |
| `ejecutar.py` | Lanzador: ejecuta, valida y mide las variantes |
| `pruebas.py` | Pruebas del contrato P01–P13 |
| `evidencias/` | Registros reales de las ejecuciones |

## Formatos

- Lote: `(id_lote, numeros)`, IDs consecutivos desde 0
- Resultado: `(id_lote, pid, cantidad, suma_parcial)`
