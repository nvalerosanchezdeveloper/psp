"""Pruebas del contrato de la P1.1 (P01-P13).

Ejecución: python pruebas.py
"""

import multiprocessing as mp
import unittest

from suma_cuadrados import (
    agregar_resultados,
    calcular_lote,
    crear_lotes,
    ejecutar_procesos,
    ejecutar_secuencial,
)

DATOS = list(range(1, 51))


class PruebasContrato(unittest.TestCase):

    def setUp(self):
        self.lotes = crear_lotes(DATOS, 7)
        self.resultados = [calcular_lote(l) for l in self.lotes]

    # P01 ------------------------------------------------------------------
    def test_P01_caso_referencia(self):
        self.assertEqual(len(self.lotes), 8)
        self.assertEqual([len(n) for _, n in self.lotes], [7] * 7 + [1])
        total_s, res_s = ejecutar_secuencial(DATOS, 7)
        total_p, res_p = ejecutar_procesos(DATOS, 7, 2)
        self.assertEqual(total_s, 42925)
        self.assertEqual(total_p, 42925)
        self.assertEqual(sum(r[2] for r in res_p), 50)
        self.assertTrue(all(isinstance(c, int) for r in res_p for c in r))

    # P02-P03 --------------------------------------------------------------
    def test_P02_lista_vacia(self):
        self.assertEqual(crear_lotes([], 2), [])
        self.assertEqual(ejecutar_secuencial([], 2), (0, []))
        self.assertEqual(ejecutar_procesos([], 2, 2), (0, []))

    def test_P03_lote_parcial_y_cero(self):
        self.assertEqual(crear_lotes([1, 2, 3], 2), [(0, [1, 2]), (1, [3])])
        self.assertEqual(ejecutar_secuencial([1, 2, 3], 2)[0], 14)
        self.assertEqual(ejecutar_procesos([1, 2, 3], 2, 2)[0], 14)
        self.assertEqual(ejecutar_secuencial([0], 1)[0], 0)
        self.assertEqual(ejecutar_procesos([0], 1, 1)[0], 0)

    # P04-P05 --------------------------------------------------------------
    def test_P04_tamano_lote_invalido(self):
        for valor in (0, -1, True):
            for datos in ([], DATOS):
                with self.subTest(lote=valor, vacia=not datos):
                    with self.assertRaises(ValueError):
                        ejecutar_secuencial(datos, valor)
                    with self.assertRaises(ValueError):
                        ejecutar_procesos(datos, valor, 2)

    def test_P05_workers_invalido(self):
        for valor in (0, -1, True):
            for datos in ([], DATOS):
                with self.subTest(workers=valor, vacia=not datos):
                    with self.assertRaises(ValueError):
                        ejecutar_procesos(datos, 7, valor)

    # P06-P08 --------------------------------------------------------------
    def _comprobar_dato_invalido(self, malo):
        datos = [1, malo, 3]
        with self.assertRaises(ValueError) as cm:
            calcular_lote((0, datos))
        self.assertIn("Lote 0", str(cm.exception))
        self.assertIn("PID", str(cm.exception))
        with self.assertRaises(ValueError):
            ejecutar_secuencial(datos, 2)
        with self.assertRaises(ValueError) as cm:
            ejecutar_procesos(datos, 2, 2)
        self.assertIn("PID", str(cm.exception))

    def test_P06_dato_negativo(self):
        self._comprobar_dato_invalido(-1)

    def test_P07_dato_booleano(self):
        self._comprobar_dato_invalido(True)

    def test_P08_dato_no_entero(self):
        self._comprobar_dato_invalido(1.5)

    # P09 ------------------------------------------------------------------
    def test_P09_orden_inverso(self):
        self.assertEqual(agregar_resultados(self.lotes, self.resultados[::-1]), 42925)

    # P10-P12 --------------------------------------------------------------
    def test_P10_duplicado(self):
        with self.assertRaises(ValueError):
            agregar_resultados(self.lotes, self.resultados + [self.resultados[0]])

    def test_P11_ausente(self):
        with self.assertRaises(ValueError):
            agregar_resultados(self.lotes, self.resultados[1:])

    def test_P12_metadatos_incoherentes(self):
        id_lote, pid, cantidad, suma = self.resultados[0]
        desconocido = self.resultados[:-1] + [(99, pid, 1, 2500)]
        mala_cantidad = [(id_lote, pid, cantidad - 1, suma)] + self.resultados[1:]
        for alterados in (desconocido, mala_cantidad):
            with self.subTest(alterados=alterados[0]):
                with self.assertRaises(ValueError):
                    agregar_resultados(self.lotes, alterados)

    # P13 ------------------------------------------------------------------
    def test_P13_fallo_cierre_y_reejecucion(self):
        with self.assertRaises(ValueError):
            ejecutar_procesos([1, -1, 3], 2, 2)
        self.assertEqual(mp.active_children(), [], "Quedan trabajadores activos")
        self.assertEqual(ejecutar_procesos(DATOS, 7, 2)[0], 42925)
        self.assertEqual(mp.active_children(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
