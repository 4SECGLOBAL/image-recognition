from fastapi import FastAPI

from AutoAnotador.api.annotator import router as annotator_router


app = FastAPI(
    title="Image Recognition - AutoAnnotator API",
    version="1.0.0",
)
app.include_router(annotator_router)
