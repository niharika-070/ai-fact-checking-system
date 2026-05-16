import qrcode

# 🚀 Direct LIVE PROJECT LINK (Streamlit)
url = "https://ai-fact-checking-system-6xgancbzgbm6fvhtj84gnh.streamlit.app/"

img = qrcode.make(url)
img.save("AI_Live_Project_QR.png")

print("QR for LIVE PROJECT generated!")