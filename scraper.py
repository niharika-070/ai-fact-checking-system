import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def is_chart_image(img_tag):
    """
    Heuristic function to detect if an image is likely a chart/graph
    """

    src = img_tag.get("src")
    alt = img_tag.get("alt")

    if not src:
        return False

    src = src.lower()
    alt = alt.lower() if alt else ""

    # Keywords that indicate charts
    chart_keywords = ["chart", "graph", "data", "plot", "trend", "figure"]

    # Words that indicate logos/icons (to skip)
    skip_keywords = ["logo", "icon", "avatar", "banner", "ads"]

    # Check for chart-related keywords
    if any(keyword in src or keyword in alt for keyword in chart_keywords):
        return True

    # Skip obvious non-chart images
    if any(keyword in src for keyword in skip_keywords):
        return False

    # Prefer large images (width/height attributes if available)
    try:
        width = int(img_tag.get("width", 0))
        height = int(img_tag.get("height", 0))
        if width > 300 and height > 200:
            return True
    except:
        pass

    return False




def scrape_article(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(res.text, "html.parser")

        # Title
        title = soup.title.text.strip() if soup.title else "No Title"

        # Text
        paragraphs = soup.find_all("p")
        text = " ".join([p.text for p in paragraphs])

        # Images
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")

            if not src:
                continue

            full_url = urljoin(url, src)

            images.append(full_url)

        return {
            "title": title,
            "text": text,
            "images": images
        }

    except Exception as e:
        return {
            "title": "error",
            "text": "",
            "images": [],
            "error": str(e)
        }