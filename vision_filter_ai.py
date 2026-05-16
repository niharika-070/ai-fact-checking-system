# vision_filter_ai.py

import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO

import pytesseract
from transformers import CLIPProcessor, CLIPModel
import torch

# -----------------------------
# LOAD CLIP MODEL (once)
# -----------------------------
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


# -----------------------------
# LOAD IMAGE
# -----------------------------
def load_image(url):
    try:
        r = requests.get(url, timeout=10)
        img = Image.open(BytesIO(r.content)).convert("RGB")
        return img
    except:
        return None


# -----------------------------
# OCR TEXT DETECTION
# -----------------------------
def text_density(img):
    try:
        text = pytesseract.image_to_string(img)
        return len(text.split())
    except:
        return 0


# -----------------------------
# CLIP CLASSIFICATION
# -----------------------------
def clip_scores(img):

    labels = [
        "a bar chart",
        "a line graph",
        "a pie chart",
        "a statistical data visualization",
        "a news infographic",
        "a website banner",
        "a logo",
        "a UI screenshot"
    ]

    inputs = processor(text=labels, images=img, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]

    chart_score = sum(probs[:4]).item()
    noise_score = sum(probs[4:]).item()

    return chart_score, noise_score


# -----------------------------
# FINAL FILTER (AI + CV)
# -----------------------------
def is_real_chart_ai(url):

    img = load_image(url)
    if img is None:
        return False

    img_np = np.array(img)
    h, w = img_np.shape[:2]

    # size filter
    if h < 250 or w < 250:
        return False

    # OCR filter
    txt = text_density(img)

    # CLIP filter
    chart_score, noise_score = clip_scores(img)

    # OpenCV structure check
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / (h * w)

    # ---------------- RULES ----------------
    if noise_score > 0.55:
        return False

    if chart_score < 0.45:
        return False

    if txt > 80:
        return False

    if edge_density < 0.02:
        return False

    return True