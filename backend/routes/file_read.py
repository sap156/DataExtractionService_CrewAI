from fastapi import APIRouter, UploadFile, File
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
import shutil
import uuid
import os

router = APIRouter()

@router.post("/read-file")
async def read_file(file: UploadFile = File(...)):
    filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_tool = FileReadTool(file_path=filename)
    agent = Agent(
        role="File Reader",
        goal="Read and interpret contents of uploaded files.",
        backstory="Reads .txt, .csv, .json files and returns usable data.",
        tools=[file_tool],
        verbose=True,
    )
    task = Task(
        description=f"Read and return the contents of the file at {filename}.",
        expected_output="File contents or structured data.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

    os.remove(filename)
    return {"result": result}
