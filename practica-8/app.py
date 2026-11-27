import os
import time
from pathlib import Path

import gradio as gr
import spaces
from transformers import pipeline

# En un Space con ZeroGPU, Hugging Face define SPACES_ZERO_GPU: el modelo va a la GPU.
# En tu computadora esa variable no existe: el modelo se queda en la CPU.
DISPOSITIVO = "cuda" if os.getenv("SPACES_ZERO_GPU") else "cpu"

clasificador = pipeline(
    "image-classification",
    model="google/mobilenet_v2_1.0_224",
    device=DISPOSITIVO,
)


@spaces.GPU
def clasificar(imagen):
    if imagen is None:
        return {}, "0.00 s"
    inicio = time.perf_counter()
    resultados = clasificador(imagen, top_k=3)
    segundos = time.perf_counter() - inicio
    etiquetas = {r["label"]: float(r["score"]) for r in resultados}
    return etiquetas, f"{segundos:.2f} s"


carpeta_ejemplos = Path("ejemplos")
ejemplos = (
    sorted(
        str(p)
        for p in carpeta_ejemplos.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    if carpeta_ejemplos.exists() and carpeta_ejemplos.is_dir()
    else None
)

demo = gr.Interface(
    fn=clasificar,
    inputs=gr.Image(type="pil", label="Tu foto"),
    outputs=[
        gr.Label(num_top_classes=3, label="Lo que ve el modelo"),
        gr.Textbox(label="Tiempo"),
    ],
    title="¿Qué hay en la foto?",
    description=(
        "MobileNetV2 (14 MB) publicado en un Space de Hugging Face. "
        "Conoce 1,000 categorías de ImageNet, con nombres en inglés."
    ),
    examples=ejemplos,
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch()