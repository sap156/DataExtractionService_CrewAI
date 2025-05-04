from fastapi import APIRouter, Query
from bs4 import BeautifulSoup
import requests
import textwrap

router = APIRouter()

@router.get("/api/selectors")
def get_selectors(url: str = Query(..., description="The webpage URL to inspect")):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")

        tags_to_check = ['h1', 'h2', 'h3', 'p', 'a', 'div', 'span', 'li']
        selector_samples = []
        seen = set()

        for tag in tags_to_check:
            for element in soup.select(tag)[:5]:  # Limit to 5 per tag
                # Prefer more specific selectors if possible
                if element.get('id'):
                    css = f"#{element.get('id')}"
                elif element.get('class'):
                    css = f"{tag}." + ".".join(element.get('class'))
                else:
                    css = tag

                # Avoid duplicates
                if css in seen:
                    continue
                seen.add(css)

                text = element.get_text(strip=True)
                if text:
                    selector_samples.append({
                        "selector": css,
                        "preview": text[:150]
                    })

        return {"url": url, "selectors": selector_samples}

    except Exception as e:
        return {"error": str(e)}
