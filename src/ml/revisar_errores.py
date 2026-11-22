import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from src.ml.texto import normalizar

datos = pd.read_csv("data/gastos_etiquetados.csv", encoding="utf-8-sig").dropna()
datos["texto"] = datos["descripcion"].apply(normalizar)

modelo = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("nb", MultinomialNB(alpha=0.5)),
])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
pred = cross_val_predict(modelo, datos["texto"], datos["categoria"], cv=cv)

real = datos["categoria"].values
print(f"Filas: {len(datos)} | Precision (validacion cruzada): {(pred == real).mean():.2%}")
print()
errores = datos[pred != real].copy()
errores["predicho"] = pred[pred != real]
errores = errores.sort_values(["categoria", "predicho"])
print(f"Errores: {len(errores)}")
for _, fila in errores.iterrows():
    print(f"{fila['categoria']} -> {fila['predicho']} | {fila['descripcion']}")
