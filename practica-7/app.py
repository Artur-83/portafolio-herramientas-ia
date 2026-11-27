from pathlib import Path
import time
import gradio as gr
import torch
from transformers import pipeline

MODEL_NAME = "google/mobilenet_v2_1.0_224"
clasificador = pipeline("image-classification", model=MODEL_NAME)

BASE_DIR = Path(__file__).resolve().parent
CARPETA_EJEMPLOS = BASE_DIR / "ejemplos"
EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

ejemplos = (
    sorted(
        str(ruta)
        for ruta in CARPETA_EJEMPLOS.iterdir()
        if ruta.is_file() and ruta.suffix.lower() in EXTENSIONES_IMAGEN
    )
    if CARPETA_EJEMPLOS.exists()
    else []
)


def clasificar(imagen):
    if imagen is None:
        return {}, "0.00 s"

    inicio = time.perf_counter()
    resultados = clasificador(imagen, top_k=3)
    fin = time.perf_counter()

    tiempo_transcurrido = fin - inicio
    etiquetas = {r["label"]: float(r["score"]) for r in resultados}

    return etiquetas, f"{tiempo_transcurrido:.2f} s"


demo = gr.Interface(
    fn=clasificar,
    inputs=gr.Image(type="pil", label="Imagen"),
    outputs=[
        gr.Label(num_top_classes=3, label="Top 3 etiquetas"),
        gr.Textbox(label="Tiempo de inferencia", lines=1),
    ],
    examples=ejemplos,
    title="¿Qué hay en la foto?",
    description=f"Clasificador de imágenes basado en el modelo {MODEL_NAME}.",
)

if __name__ == "__main__":
    demo.launch(share=True)