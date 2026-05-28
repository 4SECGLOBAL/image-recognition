from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from Inferencia.api.inference import router as inference_router


app = FastAPI(
    title="Image Recognition - Inferencia API",
    version="1.0.0",
)

app.mount(
    "/api/4/inferencia/arquivos",
    StaticFiles(directory="Inferencia"),
    name="inferencia_files",
)
app.include_router(inference_router)
