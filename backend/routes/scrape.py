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

load_dotenv()
router = APIRouter()

# ✅ OpenAI client
client = OpenAI()


# ---------------------- Scrape Request ----------------------
class ScrapeRequest(BaseModel):
    url: str
    selector: str


@router.post("/scrape")
def scrape_elements(request: ScrapeRequest):
    tool = ScrapeElementFromWebsiteTool(
        website_url=request.url,
        css_element=request.selector
    )

    agent = Agent(
        role="Web Scraper",
        goal="Extract targeted content from websites using CSS selectors.",
        backstory="A scraping expert that knows how to extract precise information from structured web pages.",
        tools=[tool],
        verbose=True,
    )

    task = Task(
        description=(
            f"Extract all elements from {request.url} using the CSS selector '{request.selector}'. "
            f"Use the ScrapeElementFromWebsiteTool for this task."
        ),
        expected_output="A clean list of extracted text elements from the provided page.",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task])
    crew.kickoff()

    try:
        output = tool._run()
        return {"result": output}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


# ---------------------- Chunking Helper ----------------------
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
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        selector_content = {}
        unique_selectors = set()

        for tag in soup.find_all():
            unique_selectors.add(tag.name)

        for tag_name in unique_selectors:
            selector_content[tag_name] = []
            for tag in soup.select(tag_name):
                text = tag.get_text(strip=True)
                if text:
                    selector_content[tag_name].append(text)

        ignored_tags = {"style", "script", "meta", "head", "link", "noscript"}
        visible_content = {k: v for k, v in selector_content.items() if k not in ignored_tags}

        # ✅ Use OpenAI with chunking
        formatted_json = chunk_prompt_and_format(visible_content, client)

        return {"result": formatted_json}

    except Exception as e:
        return {"error": str(e)}


# ---------------------- Ask API ----------------------
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
