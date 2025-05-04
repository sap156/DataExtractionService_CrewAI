from fastapi import FastAPI
from backend.routes.scrape import router as scrape_router
from backend.routes.vision import router as vision_router
from backend.routes.file_read import router as file_read_router
from backend.routes.selector_debugger import router as selector_debugger_router

from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="CrewAI Backend for Web Scraping and Extraction")

# Register endpoints
app.include_router(scrape_router, prefix="/api")
app.include_router(file_read_router, prefix="/api")
app.include_router(vision_router)
app.include_router(selector_debugger_router)


@app.get("/")
def root():
    return {"message": "CrewAI Backend is running"}
