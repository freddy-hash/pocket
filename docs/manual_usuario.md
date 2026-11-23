# Manual de Usuario — Pocket

**Pocket** es una aplicación web de finanzas personales desarrollada en Python y Streamlit que permite registrar gastos, configurar presupuestos mensuales, gestionar metas de ahorro y exportar reportes en formatos CSV y Excel.

---

## 1. Inicio de Sesión y Registro de Cuenta

1. Abre la aplicación ejecutando `streamlit run app.py` desde la raíz del proyecto.
2. Si ya tienes cuenta, ingresa tu **usuario** y **contraseña** en el formulario de inicio de sesión.
3. Si eres usuario nuevo, utiliza la pestaña o sección de **Registro** para crear tu cuenta (la contraseña se almacena cifrada mediante *hash* con `bcrypt`).
4. Una vez autenticado, verás la barra superior con tu usuario y el menú lateral de navegación.

---

## 2. Registro y Consulta de Gastos

1. En el menú lateral **Navegación**, selecciona **Gastos**.
2. Completa el formulario de registro indicando:
   - **Monto ($):** número mayor que cero (hasta dos decimales).
   - **Categoría:** categoría disponible en el sistema (por ejemplo, *Comida y bebida*).
   - **Descripción:** detalle breve del gasto.
   - **Fecha:** fecha en formato `AAAA-MM-DD` (por defecto la fecha actual).
3. Guarda el gasto para actualizar el listado de movimientos y los gráficos correspondientes.

---

## 3. Presupuestos Mensuales

1. En el menú lateral **Navegación**, selecciona **Presupuestos**.
2. **Establecer Presupuesto:**
   - Selecciona la **Categoría**.
   - Define el **Límite de Gasto ($)** mayor que cero.
   - Indica el **Mes (`AAAA-MM`)** (por defecto el mes en curso).
   - Haz clic en **Guardar Presupuesto** (si ya existía un presupuesto para esa categoría y mes, se actualiza su límite).
3. **Ver Presupuestos:**
   - Elige el mes a consultar desde el selector o ingresa manualmente otro mes en formato `AAAA-MM`.
   - Revisa la barra de progreso y el comparativo entre el **gasto acumulado** y el **límite** asignado.
   - La interfaz muestra avisos preventivos al alcanzar el **80%** del presupuesto y alertas críticas al llegar o superar el **100%**.
   - Puedes eliminar un presupuesto con el botón **Eliminar** si ya no lo necesitas.

---

## 4. Metas de Ahorro

1. En el menú lateral **Navegación**, selecciona **Metas de Ahorro**.
2. **Crear Meta:**
   - Ingresa el **Nombre de la Meta** (por ejemplo, *Fondo de emergencia* o *Viaje*).
   - Define el **Monto Objetivo ($)** mayor que cero.
   - Opcionalmente, indica un **Ahorro Inicial ($)**.
   - Haz clic en **Guardar Meta**.
3. **Mis Metas y Abonos:**
   - Consulta cada meta con su barra de progreso, el porcentaje de avance (`monto ahorrado / monto objetivo`), el monto acumulado y su fecha de creación.
   - Despliega la opción **Abonar a '<nombre>'**, ingresa el monto a abonar y confirma para sumar el aporte al saldo ahorrado.
   - Si deseas retirar una meta, usa el botón **Eliminar**.

---

## 5. Reportes Mensuales (CSV y Excel)

1. En el menú lateral **Navegación**, selecciona **Reportes**.
2. Selecciona el **mes del reporte (`AAAA-MM`)** que deseas analizar.
3. Revisa:
   - El **Total gastado en el mes**.
   - La tabla de **Resumen por Categoría** (cantidad de gastos, total gastado por categoría y porcentaje del mes).
   - El **Detalle de Gastos del Mes** (fecha, categoría, descripción y monto).
4. Descarga el reporte en el formato que prefieras:
   - **Descargar Reporte CSV** (codificado en UTF-8 con BOM para abrir sin problemas de caracteres en hojas de cálculo).
   - **Descargar Reporte Excel (`.xlsx`)** con las tablas organizadas en hojas de cálculo.
  
   docs: agregar manual de usuario
