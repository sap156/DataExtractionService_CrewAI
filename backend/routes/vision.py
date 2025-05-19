# Import necessary modules and libraries
from fastapi import APIRouter, UploadFile, File
from crewai import Agent, Task, Crew
from crewai_tools import VisionTool
from openai import OpenAI
import shutil
import uuid
import os
import logging

# Create a new FastAPI router for vision-related functionality
router = APIRouter()

# Set up logging for debugging and monitoring
logger = logging.getLogger("uvicorn")

# Initialize the OpenAI client
client = OpenAI()

@router.post("/api/vision")
async def extract_text_from_image(file: UploadFile = File(...)):
    # Save the uploaded file temporarily with a unique filename
    filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    try:
        with open(filename, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"Saved uploaded file to {filename}")

        # Step 1: Use VisionTool to extract descriptive text from the image
        vision_tool = VisionTool()
        extracted_text = vision_tool.run(image_path_url=filename)

        if not extracted_text:
            raise ValueError("No text extracted from the image.")

        logger.info(f"Raw OCR Text: {extracted_text}")

        # Step 2: Format the extracted text into structured JSON using OpenAI
        prompt = f"""You are a JSON formatter. Convert the following text into structured JSON with keys:

{extracted_text}

Return only valid JSON."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        structured_json = response.choices[0].message.content

        logger.info("Formatted JSON received")

        # Return the structured JSON result
        return {"result": structured_json}

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return {"error": str(ve)}
    except Exception as e:
        # Log and handle any errors that occur during the OCR process
        logger.error(f"OCR extraction failed: {e}")
        return {"error": str(e)}

    finally:
        # Step 3: Remove the temporary file after processing
        if os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Temporary file {filename} removed.")
