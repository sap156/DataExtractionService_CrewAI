# Import necessary modules and libraries
from fastapi import APIRouter, Query
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from crewai import Agent, Task, Crew
from crewai_tools import ScrapeElementFromWebsiteTool
from openai import OpenAI
import os
import textwrap
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Create a new FastAPI router for scraping functionality
router = APIRouter()

# Initialize the OpenAI client
client = OpenAI()


# ---------------------- Scrape Request ----------------------
# Define a Pydantic model for the scrape request
class ScrapeRequest(BaseModel):
    url: str  # The URL of the webpage to scrape
    selector: str  # The CSS selector to target specific elements


@router.post("/scrape")
def scrape_elements(request: ScrapeRequest):
    # Initialize the scraping tool with the provided URL and selector
    tool = ScrapeElementFromWebsiteTool(
        website_url=request.url,
        css_element=request.selector
    )

    # Create an Agent with a specific role and goal for web scraping
    agent = Agent(
        role="Web Scraper",
        goal="Extract targeted content from websites using CSS selectors.",
        backstory="A scraping expert that knows how to extract precise information from structured web pages.",
        tools=[tool],
        verbose=True,
    )

    # Define a Task for the Agent to perform
    task = Task(
        description=(
            f"Extract all elements from {request.url} using the CSS selector '{request.selector}'. "
            f"Use the ScrapeElementFromWebsiteTool for this task."
        ),
        expected_output="A clean list of extracted text elements from the provided page.",
        agent=agent
    )

    # Create a Crew to manage the Agent and Task, and execute the task
    crew = Crew(agents=[agent], tasks=[task])
    crew.kickoff()

    try:
        # Run the scraping tool and return the output
        output = tool._run()
        return {"result": output}
    except Exception as e:
        # Handle any errors that occur during the scraping process
        return {"error": f"Tool execution failed: {str(e)}"}


# ---------------------- Chunking Helper ----------------------
# Helper function to chunk and format scraped content using OpenAI
def chunk_prompt_and_format(selector_content, client, model="gpt-4o-mini"):
    raw_text = str(selector_content)
    chunks = textwrap.wrap(raw_text, width=6000)  # safe chunk size
    formatted_chunks = []

    for i, chunk in enumerate(chunks):
        prompt = f"""Convert the following web scraped dictionary (chunk {i+1}) into structured JSON format:

{chunk}

Return ONLY valid JSON fragment."""
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        formatted_chunks.append(response.choices[0].message.content.strip())

    return "[\n" + ",\n".join(formatted_chunks) + "\n]"


# ---------------------- Scrape-All Endpoint ----------------------
@router.get("/scrape-all")
def scrape_all_elements(url: str):
    try:
        # Send a GET request to the provided URL
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all unique HTML tags from the webpage
        selector_content = {}
        unique_selectors = set()

        for tag in soup.find_all():
            unique_selectors.add(tag.name)

        # Collect text content for each unique tag
        for tag_name in unique_selectors:
            selector_content[tag_name] = []
            for tag in soup.select(tag_name):
                text = tag.get_text(strip=True)
                if text:
                    selector_content[tag_name].append(text)

        # Filter out non-visible tags
        ignored_tags = {"style", "script", "meta", "head", "link", "noscript"}
        visible_content = {k: v for k, v in selector_content.items() if k not in ignored_tags}

        # Use OpenAI to format the visible content into JSON
        formatted_json = chunk_prompt_and_format(visible_content, client)

        return {"result": formatted_json}

    except Exception as e:
        # Handle any errors that occur during the scraping process
        return {"error": str(e)}


# ---------------------- Ask API ----------------------
# Define the Ask API endpoint
class AskRequest(BaseModel):
    data: str
    question: str


@router.post("/ask")
def ask_question(request: AskRequest):
    try:
        prompt = f"""You are an AI assistant. Answer the user's question based on the following structured JSON data:

Data:
{request.data}

Question: {request.question}

Be concise and specific. If the answer isn't clear from the data, say "Not enough information."
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return {"answer": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}
