from fastapi import APIRouter, Query
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from crewai import Agent, Task, Crew
from crewai_tools import ScrapeElementFromWebsiteTool
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# ✅ Initialize OpenAI client (v1.x compatible)
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


# ---------------------- Scrape-All Endpoint ----------------------
@router.get("/scrape-all")
def scrape_all_elements(url: str):
    try:
        response = requests.get(url, timeout=10) 
        soup = BeautifulSoup(response.text, "html.parser")

        selector_content = {}
        unique_selectors = set()  # Using a set for better performance

        # Collect all unique tag selectors
        for tag in soup.find_all():
            unique_selectors.add(tag.name)

        for tag_name in unique_selectors:
            selector_content[tag_name] = []
            for tag in soup.select(tag_name):
                text = tag.get_text(strip=True)
                if text:
                    selector_content[tag_name].append(text)
        
        # Filter out non-visible tags BEFORE building the prompt
        ignored_tags = {"style", "script", "meta", "head", "link", "noscript"}
        visible_content = {k: v for k, v in selector_content.items() if k not in ignored_tags}

        # ✅ Use OpenAI to format the output
        prompt = f"""Format the following scraped data as structured JSON:

{visible_content}

Return only valid JSON.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        formatted_json = response.choices[0].message.content

        return {"result": formatted_json}

    except Exception as e:
        return {"error": str(e)}


# ---------------------- Ask API ----------------------
class AskRequest(BaseModel):
    data: str  # Structured JSON as string
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

        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}
