from fastapi import APIRouter, UploadFile, File
from crewai import Agent, Task, Crew
from crewai_tools import VisionTool
from openai import OpenAI
import shutil
import uuid
import os
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn")
client = OpenAI()

@router.post("/api/vision")
async def extract_text_from_image(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    logger.info(f"Saved uploaded file to {filename}")

    try:
        # Step 1: Run VisionTool to get descriptive text
        vision_tool = VisionTool()
        extracted_text = vision_tool.run(image_path_url=filename)

        logger.info(f"Raw OCR Text: {extracted_text}")

        # Step 2: Format the result into structured JSON using OpenAI
        prompt = f"""
You are a JSON formatter. Convert the following text into structured JSON with keys:

\"\"\"
{extracted_text}
\"\"\"

Return only valid JSON.
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        structured_json = response.choices[0].message.content

        logger.info("Formatted JSON received")

        # Step 3: Cleanup
        os.remove(filename)

        return {"result": structured_json}

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return {"error": str(e)}
