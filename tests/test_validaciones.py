"""Pruebas unitarias para el módulo de validaciones."""

import pytest
from src.utils.validaciones import (
    validar_monto,
    validar_texto_no_vacio,
    validar_contrasena,
    validar_fecha_iso,
)


def test_validar_monto_valido():
    ok, res = validar_monto("150.556")
    assert ok is True
    assert res == 150.56


def test_validar_monto_invalido():
    ok, _ = validar_monto("abc")
    assert ok is False

    ok, _ = validar_monto(-10)
    assert ok is False


def test_validar_texto_no_vacio():
    ok, res = validar_texto_no_vacio("  Hola UGB  ", "El nombre")
    assert ok is True
    assert res == "Hola UGB"

    ok, _ = validar_texto_no_vacio("   ", "El nombre")
    assert ok is False


def test_validar_contrasena():
    ok, _ = validar_contrasena("12345")
    assert ok is False  # Muy corta

    ok, _ = validar_contrasena("secreta123")
    assert ok is True


def test_validar_fecha_iso():
    ok, res = validar_fecha_iso("2026-11-17")
    assert ok is True
    assert res == "2026-11-17"

    ok, _ = validar_fecha_iso("17-11-2026")
    assert ok is False