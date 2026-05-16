import cv2
import numpy as np
import requests


def url_to_image(url):
    try:
        resp = requests.get(url, timeout=10)
        img_array = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except:
        return None


def analyze_chart_opencv(image_input):
    try:
        # -----------------------------
        # HANDLE URL OR LOCAL PATH
        # -----------------------------
        if image_input.startswith("http"):
            img = url_to_image(image_input)
        else:
            img = cv2.imread(image_input)

        if img is None:
            return {
                "chart_type": "error",
                "issues_detected": [],
                "integrity_score": 0,
                "explanation": "Image could not be loaded (URL or file issue)"
            }

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 150)

        # Detect lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

        horizontal = 0
        vertical = 0

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y1 - y2) < 10:
                    horizontal += 1
                elif abs(x1 - x2) < 10:
                    vertical += 1

        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        large = [c for c in contours if cv2.contourArea(c) > 500]

        # Chart type
        if len(large) > 5 and vertical > 0:
            chart_type = "bar chart"
        elif horizontal > 0:
            chart_type = "line chart"
        else:
            chart_type = "unknown"

        # Issues
        issues = []

        if vertical == 0 or horizontal == 0:
            issues.append("missing axes")

        if len(large) < 3:
            issues.append("insufficient data")

        # Integrity score
        score = 85

        for i in issues:
            if i == "missing axes":
                score -= 30
            elif i == "insufficient data":
                score -= 15

        score = max(0, min(100, score))

        return {
            "chart_type": chart_type,
            "issues_detected": issues,
            "integrity_score": score,
            "explanation": "OpenCV analysis with URL support"
        }

    except Exception as e:
        return {
            "chart_type": "error",
            "issues_detected": [],
            "integrity_score": 0,
            "explanation": str(e)
        }