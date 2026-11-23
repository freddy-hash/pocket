# Librerías y Dependencias — Pocket

Este documento detalla las librerías utilizadas en **Pocket** y el rol que cumple cada una dentro de la aplicación.

---

## Librerías Principales

### `streamlit`
- **Uso en Pocket:** Construcción de toda la interfaz web interactiva (formularios, pestañas, navegación lateral `st.sidebar.radio`, barras de progreso `st.progress`, alertas `st.warning` / `st.error` / `st.success`, tablas y botones de descarga `st.download_button`).
- **Motivo de elección:** Permite desarrollar interfaces de datos en Python de forma rápida y reactiva sin necesidad de montar un backend web separado ni plantillas HTML/JS complejas.

### `pandas`
- **Uso en Pocket:** Procesamiento de registros de gastos y presupuestos, agrupación por categoría, cálculo de totales y porcentajes mensuales, y exportación de reportes en formatos **CSV** y **Excel (`.xlsx`)**.
- **Motivo de elección:** Simplifica las agregaciones por categoría (`groupby`), el formateo tabular y la generación de archivos descargables desde memoria (`io.StringIO` y `io.BytesIO`).

### `bcrypt`
- **Uso en Pocket:** Generación de *hashes* seguros con *salt* al registrar usuarios y verificación de contraseñas al iniciar sesión.
- **Motivo de elección:** Evita almacenar contraseñas en texto plano en la base de datos y protege frente a ataques de fuerza bruta o tablas arcoíris.

### `pytest`
- **Uso en Pocket:** Ejecución de pruebas automatizadas para validar reglas de negocio, validaciones de entrada y operaciones de base de datos antes de integrar o entregar cambios.
- **Motivo de elección:** Ofrece una sintaxis sencilla, reportes claros de fallos y rápida ejecución en entornos locales y de colaboración en Git.

---

## Dependencias Complementarias para Exportación Excel

### `openpyxl`
- **Uso en Pocket:** Motor utilizado por `pandas.ExcelWriter` para escribir archivos Excel modernos en formato `.xlsx` desde memoria sin dejar archivos temporales en disco.
- **Motivo de elección:** Es el estándar práctico en Python para generar libros `.xlsx` compatibles con Microsoft Excel y LibreOffice Calc.

---

## Módulos de la Biblioteca Estándar de Python

- **`sqlite3`:** Conexión y consultas sobre la base de datos local `pocket.db` (`usuarios`, `categorias`, `transacciones`, `presupuestos` y `metas_ahorro`).
- **`datetime` / `math` / `re` / `io` / `pathlib`:** Validación de fechas y meses (`AAAA-MM`), control de números finitos y redondeo monetario, expresiones regulares para formatos y manejo de rutas y buffers en memoria.
