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


# --- Presupuestos ---
ok, _ = db.guardar_presupuesto(id_usuario, id_categoria, 50, "2026-11")
verificar("Presupuesto: guardar válido", ok)

ok, _ = db.guardar_presupuesto(id_usuario, id_categoria, -10, "2026-11")
verificar("Presupuesto: rechaza límite negativo", not ok)

ok, _ = db.guardar_presupuesto(id_usuario, id_categoria, "abc", "2026-11")
verificar("Presupuesto: rechaza límite que no es número", not ok)

ok, _ = db.guardar_presupuesto(id_usuario, 9999, 50, "2026-11")
verificar("Presupuesto: rechaza categoría inexistente", not ok)

ok, _ = db.guardar_presupuesto(9999, id_categoria, 50, "2026-11")
verificar("Presupuesto: rechaza usuario inexistente", not ok)

ok, _ = db.guardar_presupuesto(id_usuario, id_categoria, 50, "2026-13")
verificar("Presupuesto: rechaza mes inválido", not ok)

db.guardar_presupuesto(id_usuario, id_categoria, 80, "2026-11")
presupuestos = db.listar_presupuestos(id_usuario, "2026-11")
verificar("Presupuesto: guardar el mismo mes actualiza y no duplica", len(presupuestos) == 1)
verificar(
    "Presupuesto: listar trae categoría y límite nuevo",
    presupuestos[0]["limite"] == 80 and presupuestos[0]["categoria"] == nombre_categoria,
)

ok, _ = db.borrar_presupuesto(id_usuario, presupuestos[0]["id"])
verificar("Presupuesto: borrar el propio", ok)

ok, _ = db.borrar_presupuesto(id_usuario, presupuestos[0]["id"])
verificar("Presupuesto: no borra uno que ya no existe", not ok)

# --- Metas de ahorro ---
ok, _ = db.crear_meta(id_usuario, "Compu nueva", 200)
verificar("Meta: crear válida", ok)

ok, _ = db.crear_meta(id_usuario, "Moto", 0)
verificar("Meta: rechaza objetivo cero", not ok)

ok, _ = db.crear_meta(id_usuario, "   ", 100)
verificar("Meta: rechaza nombre vacío", not ok)

id_meta = db.listar_metas(id_usuario)[0]["id"]

ok, _ = db.abonar_meta(id_usuario, id_meta, 50)
verificar("Meta: abonar", ok)

ok, _ = db.abonar_meta(id_usuario, id_meta, -5)
verificar("Meta: rechaza abono negativo", not ok)

db.abonar_meta(id_usuario, id_meta, 25)
metas = db.listar_metas(id_usuario)
verificar(
    "Meta: los abonos se suman (75 de 200)",
    len(metas) == 1 and metas[0]["monto_ahorrado"] == 75 and metas[0]["monto_objetivo"] == 200,
)

ok, _ = db.abonar_meta(9999, id_meta, 10)
verificar("Meta: no deja abonar a la meta de otro usuario", not ok)

ok, _ = db.borrar_meta(9999, id_meta)
verificar("Meta: no deja borrar la meta de otro usuario", not ok)

ok, _ = db.borrar_meta(id_usuario, id_meta)
verificar("Meta: borrar la propia", ok)

# --- Resumen ---
shutil.rmtree(carpeta_temp, ignore_errors=True)
print(f"\n{sum(resultados)} de {len(resultados)} pruebas correctas.")