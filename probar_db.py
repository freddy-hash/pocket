import shutil
import tempfile
from pathlib import Path

from src.database import db

# Las pruebas corren sobre una COPIA temporal de pocket.db,
# así que no ensucian la base de datos real.
carpeta_temp = tempfile.mkdtemp()
copia = Path(carpeta_temp) / "pocket_prueba.db"
shutil.copy(db.RUTA_DB, copia)
db.RUTA_DB = copia

resultados = []


def verificar(descripcion, condicion):
    resultados.append(bool(condicion))
    print(("[OK]    " if condicion else "[FALLO] ") + descripcion)


# --- Categorías ---
categorias = db.listar_categorias()
verificar("Hay 8 categorías cargadas", len(categorias) == 8)
id_categoria = categorias[0]["id"] if categorias else 1
nombre_categoria = categorias[0]["nombre"] if categorias else ""

# --- Registro de usuarios ---
ok, _ = db.registrar_usuario("Usuario Prueba", "usuario_prueba", "clave123")
verificar("Registrar usuario nuevo", ok)

ok, _ = db.registrar_usuario("Usuario Prueba", "usuario_prueba", "clave123")
verificar("Rechaza usuario repetido", not ok)

ok, _ = db.registrar_usuario("Otro", "otro", "123")
verificar("Rechaza contraseña corta", not ok)

ok, _ = db.registrar_usuario("", "vacio", "clave123")
verificar("Rechaza nombre vacío", not ok)

conexion = db.conectar()
guardada = conexion.execute(
    'SELECT "contraseña" FROM usuarios WHERE usuario = ?', ("usuario_prueba",)
).fetchone()[0]
conexion.close()
verificar("La contraseña se guarda protegida (hash)", guardada != "clave123" and guardada.startswith("$2"))

# --- Inicio de sesión ---
ok, datos = db.iniciar_sesion("usuario_prueba", "clave123")
verificar("Login con datos correctos", ok and datos["usuario"] == "usuario_prueba")
id_usuario = datos["id"] if ok else None

ok, _ = db.iniciar_sesion("usuario_prueba", "otraclave")
verificar("Rechaza contraseña incorrecta", not ok)

ok, _ = db.iniciar_sesion("fantasma", "clave123")
verificar("Rechaza usuario inexistente", not ok)

# --- Gastos ---
ok, _ = db.registrar_gasto(id_usuario, 3.50, "pupusas de la esquina", id_categoria)
verificar("Registrar gasto válido", ok)

ok, _ = db.registrar_gasto(id_usuario, -5, "bus", id_categoria)
verificar("Rechaza monto negativo", not ok)

ok, _ = db.registrar_gasto(id_usuario, 0, "bus", id_categoria)
verificar("Rechaza monto cero", not ok)

ok, _ = db.registrar_gasto(id_usuario, "abc", "bus", id_categoria)
verificar("Rechaza monto que no es número", not ok)

ok, _ = db.registrar_gasto(id_usuario, "nan", "bus", id_categoria)
verificar("Rechaza monto NaN", not ok)

ok, _ = db.registrar_gasto(id_usuario, 5, "   ", id_categoria)
verificar("Rechaza descripción vacía", not ok)

ok, _ = db.registrar_gasto(id_usuario, 5, "bus", id_categoria, "25/10/2026")
verificar("Rechaza fecha con formato incorrecto", not ok)

ok, _ = db.registrar_gasto(9999, 5, "bus", id_categoria)
verificar("Rechaza usuario inexistente", not ok)

ok, _ = db.registrar_gasto(id_usuario, 5, "bus", 9999)
verificar("Rechaza categoría inexistente", not ok)

gastos = db.listar_gastos(id_usuario)
verificar(
    "Listar gastos devuelve solo el gasto válido",
    len(gastos) == 1 and gastos[0]["monto"] == 3.5 and gastos[0]["categoria"] == nombre_categoria,
)

# --- Resumen ---
shutil.rmtree(carpeta_temp, ignore_errors=True)
print(f"\n{sum(resultados)} de {len(resultados)} pruebas correctas.")