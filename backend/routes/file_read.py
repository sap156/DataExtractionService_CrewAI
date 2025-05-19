# Import necessary modules and libraries
from fastapi import APIRouter, UploadFile, File
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
import shutil
import uuid
import os

# Create a new FastAPI router for file reading functionality
router = APIRouter()

@router.post("/read-file")
async def read_file(file: UploadFile = File(...)):
    # Generate a unique filename for the uploaded file and save it temporarily
    filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Initialize the FileReadTool to process the uploaded file
    file_tool = FileReadTool(file_path=filename)

    # Create an Agent with a specific role and goal for reading files
    agent = Agent(
        role="File Reader",
        goal="Read and interpret contents of uploaded files.",
        backstory="Reads .txt, .csv, .json files and returns usable data.",
        tools=[file_tool],
        verbose=True,
    )

    # Define a Task for the Agent to perform
    task = Task(
        description=f"Read and return the contents of the file at {filename}.",
        expected_output="File contents or structured data.",
        agent=agent,
    )

    # Create a Crew to manage the Agent and Task, and execute the task
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

    # Remove the temporary file after processing
    os.remove(filename)

    # Return the result of the file reading operation
    return {"result": result}
