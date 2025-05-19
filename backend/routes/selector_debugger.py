# Import necessary modules and libraries
from fastapi import APIRouter, Query
from bs4 import BeautifulSoup
import requests
import textwrap

# Create a new FastAPI router for selector debugging functionality
router = APIRouter()

@router.get("/api/selectors")
def get_selectors(url: str = Query(..., description="The webpage URL to inspect")):
    try:
        # Send a GET request to the provided URL
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")

        # Define a list of tags to inspect for CSS selectors
        tags_to_check = ['h1', 'h2', 'h3', 'p', 'a', 'div', 'span', 'li']
        selector_samples = []
        seen = set()

        # Iterate through each tag and collect sample selectors
        for tag in tags_to_check:
            for element in soup.select(tag)[:5]:  # Limit to 5 elements per tag
                # Generate a CSS selector for the element
                if element.get('id'):
                    css = f"#{element.get('id')}"
                elif element.get('class'):
                    css = f"{tag}." + ".".join(element.get('class'))
                else:
                    css = tag

                # Avoid duplicate selectors
                if css in seen:
                    continue
                seen.add(css)

                # Collect a preview of the element's text content
                text = element.get_text(strip=True)
                if text:
                    selector_samples.append({
                        "selector": css,
                        "preview": text[:150]  # Limit preview to 150 characters
                    })

        # Return the collected selectors and their previews
        return {"url": url, "selectors": selector_samples}

    except Exception as e:
        # Handle any errors that occur during the selector inspection process
        return {"error": str(e)}
