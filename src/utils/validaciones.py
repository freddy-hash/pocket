"""
Módulo de validaciones generales para la aplicación Pocket.
Contiene funciones puras para validar datos de entrada (montos, textos, contraseñas, fechas).
"""

from datetime import datetime
import math
import re


def validar_monto(valor: str | float | int) -> tuple[bool, float | str]:
    """Valida que un monto sea un número finito mayor que cero con máximo 2 decimales.
    Devuelve (True, monto_redondeado) o (False, mensaje_error).
    """
    try:
        monto = float(valor)
    except (TypeError, ValueError):
        return False, "El monto debe ser un número válido."

    if not math.isfinite(monto):
        return False, "El monto debe ser un número válido."

    monto = round(monto, 2)
    if monto <= 0:
        return False, "El monto debe ser mayor que cero."

    return True, monto


def validar_texto_no_vacio(texto: str, nombre_campo: str = "El campo") -> tuple[bool, str]:
    """Valida que un texto no esté vacío después de quitar espacios."""
    texto_limpio = (texto or "").strip()
    if not texto_limpio:
        return False, f"{nombre_campo} no puede estar vacío."
    return True, texto_limpio


def validar_contrasena(contrasena: str) -> tuple[bool, str]:
    """Valida que la contraseña cumpla con los requisitos mínimos de seguridad."""
    if not contrasena:
        return False, "La contraseña no puede estar vacía."
    
    if len(contrasena) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
        
    if len(contrasena.encode("utf-8")) > 72:
        return False, "La contraseña es demasiado larga."
        
    return True, "Contraseña válida."


def validar_fecha_iso(fecha_str: str) -> tuple[bool, str]:
    """Valida que una fecha esté en formato AAAA-MM-DD."""
    try:
        fecha_validada = datetime.strptime(str(fecha_str), "%Y-%m-%d").date().isoformat()
        return True, fecha_validada
    except ValueError:
        return False, "La fecha debe tener el formato AAAA-MM-DD."