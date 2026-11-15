import sqlite3
import bcrypt
import math
from datetime import date, datetime
from pathlib import Path

# Ruta a la base de datos: pocket/data/pocket.db
RUTA_DB = Path(__file__).resolve().parent.parent.parent / "data" / "pocket.db"

# Tablas nuevas de la Entrega 2 (se crean solas si no existen)
SQL_TABLAS_NUEVAS = """
CREATE TABLE IF NOT EXISTS presupuestos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    limite REAL NOT NULL CHECK (limite > 0),
    mes TEXT NOT NULL,
    UNIQUE (id_usuario, id_categoria, mes),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id)
);

CREATE TABLE IF NOT EXISTS metas_ahorro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    monto_objetivo REAL NOT NULL CHECK (monto_objetivo > 0),
    monto_ahorrado REAL NOT NULL DEFAULT 0 CHECK (monto_ahorrado >= 0),
    fecha_creacion TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);
"""

def conectar():
    """Abre la conexión a pocket.db y la devuelve."""
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row  # permite leer columnas por nombre
    conexion.executescript(SQL_TABLAS_NUEVAS)  # crea las tablas nuevas si no existen
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


        
def _numero_positivo(valor):
    """Convierte a número con 2 decimales. Devuelve None si no es válido o no es mayor que cero."""
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(valor):
        return None
    valor = round(valor, 2)
    return valor if valor > 0 else None


def _mes_valido(mes):
    """Devuelve el mes en formato AAAA-MM (el actual si es None) o None si es inválido."""
    if mes is None:
        return date.today().strftime("%Y-%m")
    try:
        return datetime.strptime(str(mes), "%Y-%m").strftime("%Y-%m")
    except ValueError:
        return None


# ---------- Presupuestos ----------

def guardar_presupuesto(id_usuario, id_categoria, limite, mes=None):
    """Crea o actualiza el límite mensual de una categoría. Devuelve (True/False, mensaje)."""
    limite = _numero_positivo(limite)
    if limite is None:
        return False, "El límite debe ser un número mayor que cero."

    mes = _mes_valido(mes)
    if mes is None:
        return False, "El mes debe tener el formato AAAA-MM."

    conexion = conectar()
    try:
        if conexion.execute("SELECT 1 FROM usuarios WHERE id = ?", (id_usuario,)).fetchone() is None:
            return False, "El usuario no existe."
        if conexion.execute("SELECT 1 FROM categorias WHERE id = ?", (id_categoria,)).fetchone() is None:
            return False, "La categoría no existe."

        conexion.execute(
            "INSERT INTO presupuestos (id_usuario, id_categoria, limite, mes) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id_usuario, id_categoria, mes) DO UPDATE SET limite = excluded.limite",
            (id_usuario, id_categoria, limite, mes),
        )
        conexion.commit()
        return True, "Presupuesto guardado correctamente."
    finally:
        conexion.close()


def listar_presupuestos(id_usuario, mes=None):
    """Devuelve los presupuestos de un usuario en un mes (AAAA-MM, por defecto el actual)."""
    mes = _mes_valido(mes)
    if mes is None:
        return []

    conexion = conectar()
    try:
        filas = conexion.execute(
            "SELECT p.id, p.id_categoria, c.nombre AS categoria, p.limite, p.mes "
            "FROM presupuestos p "
            "JOIN categorias c ON c.id = p.id_categoria "
            "WHERE p.id_usuario = ? AND p.mes = ? "
            "ORDER BY c.id",
            (id_usuario, mes),
        ).fetchall()
        return [dict(fila) for fila in filas]
    finally:
        conexion.close()


def borrar_presupuesto(id_usuario, id_presupuesto):
    """Borra un presupuesto del usuario. Devuelve (True/False, mensaje)."""
    conexion = conectar()
    try:
        cursor = conexion.execute(
            "DELETE FROM presupuestos WHERE id = ? AND id_usuario = ?",
            (id_presupuesto, id_usuario),
        )
        conexion.commit()
        if cursor.rowcount == 0:
            return False, "El presupuesto no existe."
        return True, "Presupuesto eliminado."
    finally:
        conexion.close()


# ---------- Metas de ahorro ----------

def crear_meta(id_usuario, nombre, monto_objetivo):
    """Crea una meta de ahorro. Devuelve (True/False, mensaje)."""
    nombre = (nombre or "").strip()
    if not nombre:
        return False, "La meta necesita un nombre."

    monto_objetivo = _numero_positivo(monto_objetivo)
    if monto_objetivo is None:
        return False, "El monto objetivo debe ser un número mayor que cero."

    conexion = conectar()
    try:
        if conexion.execute("SELECT 1 FROM usuarios WHERE id = ?", (id_usuario,)).fetchone() is None:
            return False, "El usuario no existe."

        conexion.execute(
            "INSERT INTO metas_ahorro (id_usuario, nombre, monto_objetivo, fecha_creacion) "
            "VALUES (?, ?, ?, ?)",
            (id_usuario, nombre, monto_objetivo, date.today().isoformat()),
        )
        conexion.commit()
        return True, "Meta creada correctamente."
    finally:
        conexion.close()


def listar_metas(id_usuario):
    """Devuelve las metas de ahorro de un usuario como lista de diccionarios."""
    conexion = conectar()
    try:
        filas = conexion.execute(
            "SELECT id, nombre, monto_objetivo, monto_ahorrado, fecha_creacion "
            "FROM metas_ahorro WHERE id_usuario = ? ORDER BY id",
            (id_usuario,),
        ).fetchall()
        return [dict(fila) for fila in filas]
    finally:
        conexion.close()


def abonar_meta(id_usuario, id_meta, monto):
    """Suma un abono a una meta del usuario. Devuelve (True/False, mensaje)."""
    monto = _numero_positivo(monto)
    if monto is None:
        return False, "El abono debe ser un número mayor que cero."

    conexion = conectar()
    try:
        cursor = conexion.execute(
            "UPDATE metas_ahorro SET monto_ahorrado = ROUND(monto_ahorrado + ?, 2) "
            "WHERE id = ? AND id_usuario = ?",
            (monto, id_meta, id_usuario),
        )
        conexion.commit()
        if cursor.rowcount == 0:
            return False, "La meta no existe."
        return True, "Abono registrado correctamente."
    finally:
        conexion.close()


def borrar_meta(id_usuario, id_meta):
    """Borra una meta del usuario. Devuelve (True/False, mensaje)."""
    conexion = conectar()
    try:
        cursor = conexion.execute(
            "DELETE FROM metas_ahorro WHERE id = ? AND id_usuario = ?",
            (id_meta, id_usuario),
        )
        conexion.commit()
        if cursor.rowcount == 0:
            return False, "La meta no existe."
        return True, "Meta eliminada."
    finally:
        conexion.close()
        

