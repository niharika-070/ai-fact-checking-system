from google import genai
from PIL import Image
import json
import os

# 🔑 Use your API key (better: use environment variable)
client = genai.Client(api_key="AIzaSyAd6CYKGiGzSqG2Y47_bidgChb2iVMG2NA")


# -----------------------------
# 🔹 PROMPT
# -----------------------------
def get_prompt():
    return """
    You are an expert in detecting misleading data visualizations.

    Analyze this chart image and respond STRICTLY in JSON format.

    Detect:
    - chart_type (bar, line, pie, etc.)
    - issues_detected (list):
        - truncated Y-axis
        - inverted axis
        - missing labels
        - cherry-picked data
    - explanation

    Output format:
    {
        "chart_type": "",
        "issues_detected": [],
        "explanation": ""
    }
    """


# -----------------------------
# 🔹 LOCAL IMAGE ANALYSIS (MAIN WORKING FUNCTION)
# -----------------------------
def analyze_chart_local(image_path):
    try:
        print("Loading image from:", image_path)

        # Load image
        img = Image.open(image_path)
        print("Format:", img.format)

        img = img.convert("RGB")

        # Call Gemini
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=[get_prompt(), img]
        )

        # Try parsing JSON
        try:
            return json.loads(response.text)
        except:
            return {
                "chart_type": "unknown",
                "issues_detected": [],
                "explanation": response.text
            }

    except Exception as e:
        return {
            "chart_type": "error",
            "issues_detected": [],
            "explanation": str(e)
        }


# -----------------------------
# 🔹 OPTIONAL: URL IMAGE SUPPORT (ADVANCED)
# -----------------------------
def analyze_chart_url(image_url):
    import requests
    from io import BytesIO

    try:
        response = requests.get(image_url, timeout=5)

        content_type = response.headers.get("Content-Type", "")

        if "image" not in content_type:
            return {
                "chart_type": "invalid",
                "issues_detected": [],
                "explanation": f"Not an image (Content-Type: {content_type})"
            }

        try:
            img = Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            return {
                "chart_type": "invalid",
                "issues_detected": [],
                "explanation": f"Image load failed: {str(e)}"
            }

        ai_response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=[get_prompt(), img]
        )

        try:
            return json.loads(ai_response.text)
        except:
            return {
                "chart_type": "unknown",
                "issues_detected": [],
                "explanation": ai_response.text
            }

    except Exception as e:
        return {
            "chart_type": "error",
            "issues_detected": [],
            "explanation": str(e)
        }