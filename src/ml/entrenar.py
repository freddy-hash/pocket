import os

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from src.ml.texto import normalizar

RUTA_CSV = os.path.join("data", "gastos_etiquetados.csv")
RUTA_MODELO = os.path.join("models", "clasificador.joblib")


def main():
    datos = pd.read_csv(RUTA_CSV, encoding="utf-8-sig").dropna()
    datos["texto"] = datos["descripcion"].apply(normalizar)

    X_train, X_test, y_train, y_test = train_test_split(
        datos["texto"],
        datos["categoria"],
        test_size=0.2,
        random_state=42,
        stratify=datos["categoria"],
    )

    modelo = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("nb", MultinomialNB(alpha=0.5)),
    ])
    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)
    print(f"Filas de entrenamiento: {len(X_train)} | Filas de prueba: {len(X_test)}")
    print(f"Precision: {precision:.2%}")
    print(classification_report(y_test, predicciones, zero_division=0))

    os.makedirs("models", exist_ok=True)
    joblib.dump(modelo, RUTA_MODELO)
    print(f"Modelo guardado en {RUTA_MODELO}")


if __name__ == "__main__":
    main()
