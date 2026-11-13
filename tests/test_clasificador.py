import sys

from src.ml.clasificador import sugerir_categoria

CATEGORIAS = [
    "Comida y bebida",
    "Transporte",
    "Servicios basicos",
    "Educación y materiales",
    "Entretenimiento y salidas",
    "Ropa y compras personales",
    "Gastos medicos",
    "Hogar renta y ahorro",
]


def test_comida():
    assert sugerir_categoria("tamales de elote") == "Comida y bebida"


def test_transporte():
    assert sugerir_categoria("pasaje del bus") == "Transporte"


def test_servicios():
    assert sugerir_categoria("recibo de luz") == "Servicios basicos"


def test_educacion():
    assert sugerir_categoria("cuaderno universitario") == "Educación y materiales"


def test_entretenimiento():
    assert sugerir_categoria("cine con amigos") == "Entretenimiento y salidas"


def test_ropa():
    assert sugerir_categoria("camisa nueva") == "Ropa y compras personales"


def test_medicos():
    assert sugerir_categoria("consulta medica") == "Gastos medicos"


def test_hogar():
    assert sugerir_categoria("pago de renta") == "Hogar renta y ahorro"


def test_descripcion_vacia():
    assert sugerir_categoria("") is None


def test_solo_espacios():
    assert sugerir_categoria("     ") is None


def test_texto_raro():
    assert sugerir_categoria("xqzw") is None


def test_solo_simbolos():
    assert sugerir_categoria("!!!???") is None


def test_no_es_texto():
    assert sugerir_categoria(None) is None
    assert sugerir_categoria(123) is None


def test_devuelve_categoria_valida():
    resultado = sugerir_categoria("PUPUSAS de queso!!")
    assert resultado in CATEGORIAS


if __name__ == "__main__":
    fallos = 0
    for nombre, funcion in list(globals().items()):
        if nombre.startswith("test_") and callable(funcion):
            try:
                funcion()
                print("OK   ", nombre)
            except AssertionError:
                print("FALLO", nombre)
                fallos += 1
    print(f"\nFallos: {fallos}")
    sys.exit(1 if fallos else 0)
