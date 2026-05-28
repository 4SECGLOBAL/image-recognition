from fastapi import FastAPI

from Avaliador.api.trainer import router as trainer_router


app = FastAPI(
    title="Image Recognition - Avaliador API",
    version="1.0.0",
)
app.include_router(trainer_router)
