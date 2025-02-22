import json
from datetime import datetime

def save_json_summary():
    summary = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "project_stats": {
            "categories": [
                "ekonomi", "teknoloji", "siyaset", "spor", "sağlık",
                "eğitim", "bilim", "çevre", "kültür-sanat"
            ],
            "analysis_types": [
                "duygu analizi",
                "etkileşim analizi",
                "kategori analizi",
                "etki analizi"
            ],
            "visualizations": [
                "category_sentiment.png",
                "sentiment_interaction.png", 
                "popular_categories.png",
                "category_impact.png",
                "top_impact_news.png"
            ]
        }
    }
    
    with open('data/analysis/summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    save_json_summary() 