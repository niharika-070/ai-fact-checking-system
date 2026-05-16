from scraper import scrape_article
from vision_opencv import analyze_chart_opencv
from utils import is_chart_image


def run_pipeline(url):
    data = scrape_article(url)

    print("\n🔹 Article Title:", data["title"])

    results = []

    for img_url in data["images"]:
        if not is_chart_image(img_url):
            continue

        print("\n📊 Analyzing:", img_url)

        result = analyze_chart_opencv(img_url)

        results.append(result)

    # If no chart images found
    if not results:
        return {
            "status": "no_charts_found",
            "title": data["title"],
            "integrity_scores": []
        }

    # Compute final score
    scores = [r["integrity_score"] for r in results if "integrity_score" in r]

    final_score = sum(scores) / len(scores)

    return {
        "title": data["title"],
        "charts_analyzed": len(results),
        "final_integrity_score": round(final_score, 2),
        "details": results
    }


# ---------------- RUN ----------------
if __name__ == "__main__":
    url = input("Enter news URL: ")
    output = run_pipeline(url)

    print("\n================ RESULT ================\n")
    print(output)