from fastapi import FastAPI

from DataScrapper.api.datascrapper import router as datascrapper_router


app = FastAPI(
    title="Image Recognition - DataScrapper API",
    version="1.0.0",
)
app.include_router(datascrapper_router)
