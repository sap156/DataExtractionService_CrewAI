from fastapi import APIRouter, UploadFile, File
from crewai import Agent, Task, Crew
from crewai_tools import VisionTool
import shutil
import uuid
import os

router = APIRouter()

@router.post("/ocr")
async def extract_text_from_image(file: UploadFile = File(...)):
    filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    vision_tool = VisionTool()
    agent = Agent(
        role="OCR Agent",
        goal="Extract text from image files.",
        backstory="Expert in reading image text using VisionTool.",
        tools=[vision_tool],
        verbose=True,
    )
    task = Task(
        description=f"Extract text from image at path {filename}.",
        expected_output="Extracted text from image.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

    os.remove(filename)
    return {"result": result}
