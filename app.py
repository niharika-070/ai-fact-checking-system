import streamlit as st
import time
import numpy as np
import cv2
import requests
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

from scraper import scrape_article
from vision_opencv import analyze_chart_opencv
from vision_filter_ai import is_real_chart_ai

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="AI Fact-Checker",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================
# ULTRA MODERN UI THEME
# =============================
st.markdown("""
<style>

/* Animated background */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Glass cards */
.block-container {
    padding-top: 2rem;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(15px);
    box-shadow: 0 0 25px rgba(0,255,213,0.15);
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #00ffd5, #00aaff);
    color: black;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px #00ffd5;
}

/* Titles */
h1, h2, h3 {
    color: #00ffd5 !important;
}

/* Expander styling */
details {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 10px !important;
}

</style>
""", unsafe_allow_html=True)


# =============================
# SIDEBAR CONTROL PANEL
# =============================
st.sidebar.title("⚙️ Control Panel")
st.sidebar.write("Tune analysis settings")

show_debug = st.sidebar.toggle("Show Debug Info", value=True)
run_animation = st.sidebar.toggle("AI Live Animation", value=True)


# =============================
# IMAGE LOADER
# =============================
def load_image(url):
    try:
        resp = requests.get(url, timeout=10)
        img_array = np.frombuffer(resp.content, np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except:
        return None


# =============================
# SMART FILTER
# =============================
def is_real_chart(url):
    img = load_image(url)
    if img is None:
        return False

    h, w = img.shape[:2]
    if h < 300 or w < 300:
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    density = np.sum(edges > 0) / (h * w)

    if density < 0.02 or density > 0.6:
        return False

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return len(contours) > 6


# =============================
# GAUGE (FANCY)
# =============================
def score_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": "Integrity Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00ffd5"},
            "steps": [
                {"range": [0, 40], "color": "#ff4d4d"},
                {"range": [40, 70], "color": "#ffcc00"},
                {"range": [70, 100], "color": "#2ecc71"},
            ]
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    return fig


# =============================
# PDF REPORT
# =============================
def generate_pdf(title, score, charts):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="AI Fact-Checking Report", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Title: {title}", ln=True)
    pdf.cell(200, 10, txt=f"Integrity Score: {score}", ln=True)
    pdf.cell(200, 10, txt=f"Generated: {datetime.now()}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Chart Analysis:", ln=True)

    for i, c in enumerate(charts):
        pdf.multi_cell(0, 10, txt=f"""
Chart {i+1}
Type: {c['chart_type']}
Score: {c['integrity_score']}
Issues: {', '.join(c['issues_detected'])}
""")

    path = "report.pdf"
    pdf.output(path)
    return path


# =============================
# PIPELINE (CORE)
# =============================
def run_pipeline(url):

    data = scrape_article(url)
    images = data.get("images", [])

    results = []
    seen = set()

    progress = st.progress(0)
    status = st.empty()

    total = len(images)

    for i, img_url in enumerate(images):

        if run_animation:
            status.write(f"🧠 AI scanning image {i+1}/{total}")
            time.sleep(0.4)

        if img_url in seen:
            continue
        seen.add(img_url)

        if not is_real_chart_ai(img_url):
            continue

        result = analyze_chart_opencv(img_url)
        result["image_url"] = img_url
        results.append(result)

        progress.progress((i + 1) / total if total else 1)

    status.success("Analysis Complete ✔")

    if len(results) == 0:
        return data["title"], 0, []

    scores = [r["integrity_score"] for r in results]
    final_score = sum(scores) / len(scores)

    return data["title"], round(final_score, 2), results


# =============================
# HERO UI
# =============================
st.title("🧠 AI FACT-CHECKING ENGINE")
st.write("Detect misleading charts using Computer Vision + Structural Integrity Scoring")


url = st.text_input("Paste News Article URL")

if st.button("🚀 Analyze Now"):

    with st.spinner("Initializing AI pipeline..."):
        title, score, charts = run_pipeline(url)

    st.balloons()

    # =============================
    # TOP METRICS
    # =============================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Charts Detected", len(charts))

    with col2:
        st.metric("Integrity Score", f"{score}/100")

    with col3:
        st.metric("AI Status", "ACTIVE")

    # =============================
    # GAUGE
    # =============================
    st.plotly_chart(score_gauge(score), use_container_width=True)

    # =============================
    # DEBUG INFO
    # =============================
    if show_debug:
        st.write("📌 Charts Found:", len(charts))

    # =============================
    # CHART DISPLAY
    # =============================
    for i, c in enumerate(charts):

        with st.expander(f"📊 Chart {i+1} | Score {c['integrity_score']}"):

            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(c["image_url"], use_container_width=True)

            with col2:
                st.write("### Type:", c["chart_type"])
                st.write("### Issues:")
                st.write(c["issues_detected"])
                st.write("### Score:", c["integrity_score"])

    # =============================
    # PDF DOWNLOAD
    # =============================
    pdf_path = generate_pdf(title, score, charts)

    with open(pdf_path, "rb") as f:
        st.download_button(
            "📄 Download AI Report",
            f,
            file_name="fact_check_report.pdf",
            mime="application/pdf"
        )