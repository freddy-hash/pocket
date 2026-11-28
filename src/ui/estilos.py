import streamlit as st

_CSS = """
<style>
h1, h2, h3 { color: #10B981; }

[data-testid="stForm"], [data-testid="stExpander"] {
    border-radius: 12px;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #10B981;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #10B981;
    color: white;
    border-color: #10B981;
}

[data-testid="stMetric"] {
    background-color: rgba(16, 185, 129, 0.12);
    border-radius: 12px;
    padding: 12px 16px;
}
</style>
"""


def aplicar_estilos():
    """Inyecta el CSS de Pocket. Funciona en modo claro y oscuro."""
    st.markdown(_CSS, unsafe_allow_html=True)