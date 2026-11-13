import os

import joblib

from src.ml.texto import normalizar

RUTA_MODELO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models",
    "clasificador.joblib",
)

_modelo = None
_intentado = False


def _cargar_modelo():
    """Carga el modelo una sola vez. Si falla, devuelve None."""
    global _modelo, _intentado
    if not _intentado:
        _intentado = True
        try:
            _modelo = joblib.load(RUTA_MODELO)
        except Exception:
            _modelo = None
    return _modelo


def sugerir_categoria(descripcion):
    """Recibe un texto y devuelve el nombre exacto de la categoria, o None."""
    try:
        if not isinstance(descripcion, str):
            return None
        texto = normalizar(descripcion)
        if not texto:
            return None
        modelo = _cargar_modelo()
        if modelo is None:
            return None
        # Si ninguna palabra del texto existe en el vocabulario, no se puede clasificar.
        vector = modelo.named_steps["tfidf"].transform([texto])
        if vector.nnz == 0:
            return None
        return str(modelo.predict([texto])[0])
    except Exception:
        return None
