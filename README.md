# Pocket

Aplicación web de finanzas personales con categorización inteligente de gastos.
Proyecto final de Programación Computacional III, Universidad Gerardo Barrios.

Equipo: Los Ponis
Coordinador: Freddy Isai Solis Gomez

## Integrantes y roles

- Freddy Isai Solis Gomez: base de datos y lógica, análisis y gráficos
- Dixy Gimena: machine learning
- Angely Gissel Rivera Sandoval: interfaz y documentación

## Qué hace

Registra gastos en dólares, sugiere la categoría de cada gasto automáticamente con machine learning, y muestra gráficos de en qué se gasta el dinero.

## Categorías de gasto

Comida y bebida, Transporte, Servicios básicos, Educación y materiales, Entretenimiento y salidas, Ropa y compras personales, Gastos médicos, Hogar renta y ahorro.

## Instalación

```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Pruebas

```
python probar_db.py
```