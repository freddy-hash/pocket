import sqlite3
import bcrypt
import math
from datetime import date, datetime
from pathlib import Path

# Ruta a la base de datos: pocket/data/pocket.db
RUTA_DB = Path(__file__).resolve().parent.parent.parent / "data" / "pocket.db"


def conectar():
    """Abre la conexión a pocket.db y la devuelve."""
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row  # permite leer columnas por nombre
    return conexion

def registrar_usuario(nombre, usuario, contrasena):
    """Registra un usuario nuevo. Devuelve (True/False, mensaje)."""
    nombre = nombre.strip()
    usuario = usuario.strip()

    if not nombre or not usuario or not contrasena:
        return False, "Todos los campos son obligatorios."
    if len(contrasena) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
    if len(contrasena.encode("utf-8")) > 72:
        return False, "La contraseña es demasiado larga."

    # Se guarda el hash, nunca la contraseña real
    hash_contrasena = bcrypt.hashpw(
        contrasena.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    conexion = conectar()
    try:
        conexion.execute(
            'INSERT INTO usuarios (nombre, usuario, "contraseña") VALUES (?, ?, ?)',
            (nombre, usuario, hash_contrasena),
        )
        conexion.commit()
        return True, "Usuario registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "Ese usuario ya existe."
    finally:
        conexion.close()

def iniciar_sesion(usuario, contrasena):
    """Verifica usuario y contraseña. Devuelve (True, datos) o (False, mensaje)."""
    usuario = usuario.strip()

    if not usuario or not contrasena:
        return False, "Escribe tu usuario y contraseña."
    if len(contrasena.encode("utf-8")) > 72:
        return False, "Usuario o contraseña incorrectos."

    conexion = conectar()
    try:
        fila = conexion.execute(
            'SELECT id, nombre, usuario, "contraseña" AS hash FROM usuarios WHERE usuario = ?',
            (usuario,),
        ).fetchone()
    finally:
        conexion.close()

    # Mismo mensaje si no existe el usuario o si la contraseña falla
    if fila is None:
        return False, "Usuario o contraseña incorrectos."

    if bcrypt.checkpw(contrasena.encode("utf-8"), fila["hash"].encode("utf-8")):
        return True, {"id": fila["id"], "nombre": fila["nombre"], "usuario": fila["usuario"]}

    return False, "Usuario o contraseña incorrectos."


def registrar_gasto(id_usuario, monto, descripcion, id_categoria, fecha=None):
    """Registra un gasto. Devuelve (True/False, mensaje). Fecha en formato AAAA-MM-DD."""
    descripcion = (descripcion or "").strip()

    try:
        monto = float(monto)
    except (TypeError, ValueError):
        return False, "El monto debe ser un número."
    if not math.isfinite(monto):
        return False, "El monto debe ser un número válido."
    monto = round(monto, 2)
    if monto <= 0:
        return False, "El monto debe ser mayor que cero."

    if not descripcion:
        return False, "La descripción no puede estar vacía."

    if fecha is None:
        fecha = date.today().isoformat()
    else:
        try:
            fecha = datetime.strptime(str(fecha), "%Y-%m-%d").date().isoformat()
        except ValueError:
            return False, "La fecha debe tener el formato AAAA-MM-DD."

    conexion = conectar()
    try:
        if conexion.execute("SELECT 1 FROM usuarios WHERE id = ?", (id_usuario,)).fetchone() is None:
            return False, "El usuario no existe."
        if conexion.execute("SELECT 1 FROM categorias WHERE id = ?", (id_categoria,)).fetchone() is None:
            return False, "La categoría no existe."

        conexion.execute(
            "INSERT INTO transacciones (monto, descripcion, fecha, id_categoria, id_usuario) "
            "VALUES (?, ?, ?, ?, ?)",
            (monto, descripcion, fecha, id_categoria, id_usuario),
        )
        conexion.commit()
        return True, "Gasto registrado correctamente."
    finally:
        conexion.close()


def listar_gastos(id_usuario):
    """Devuelve los gastos de un usuario (más recientes primero) como lista de diccionarios."""
    conexion = conectar()
    try:
        filas = conexion.execute(
            "SELECT t.id, t.fecha, t.monto, t.descripcion, c.nombre AS categoria "
            "FROM transacciones t "
            "JOIN categorias c ON c.id = t.id_categoria "
            "WHERE t.id_usuario = ? "
            "ORDER BY t.fecha DESC, t.id DESC",
            (id_usuario,),
        ).fetchall()
        return [dict(fila) for fila in filas]
    finally:
        conexion.close()


def listar_categorias():
    """Devuelve las categorías como lista de diccionarios (id, nombre). La interfaz la usa para el menú."""
    conexion = conectar()
    try:
        filas = conexion.execute("SELECT id, nombre FROM categorias ORDER BY id").fetchall()
        return [dict(fila) for fila in filas]
    finally:
        conexion.close()

        

