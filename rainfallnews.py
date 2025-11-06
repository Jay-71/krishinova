import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

def get_latest_agriculture_news_maharashtra(limit=15, translate_to_english=False):
    # Query: Agriculture + Maharashtra in Marathi
    query = "(कृषी OR शेतकरी OR पिके OR शेती) महाराष्ट्र"
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=mr&gl=IN&ceid=IN:mr"

    # Fetch RSS feed
    resp = requests.get(rss_url)
    soup = BeautifulSoup(resp.content, "xml")
    items = soup.find_all("item")[:limit]

    if not items:
        print("❌ No news found.")
        return []

    print(f"\n📰 LATEST AGRICULTURE NEWS FROM MAHARASHTRA ({len(items)} results)\n" + "="*60)

    news_list = []
    for i, item in enumerate(items, start=1):
        title_marathi = item.title.text
        link = item.link.text
        pub_date = item.pubDate.text if item.pubDate else "N/A"
        source_tag = item.find("source")
        source_name = source_tag.text if source_tag else "Unknown Source"
        source_url = source_tag["url"] if source_tag and source_tag.has_attr("url") else ""

        title_english = None
        if translate_to_english:
            try:
                title_english = GoogleTranslator(source='mr', target='en').translate(title_marathi)
            except Exception:
                title_english = "Translation error"

        print(f"\n{i}. 🟢 {title_marathi}")
        if title_english:
            print(f"   🔹 English: {title_english}")
        print(f"   🗓️ Date: {pub_date}")
        print(f"   📰 Source: {source_name} ({source_url})")
        print(f"   🌐 Read full article: {link}")

        news_list.append({
            "title_marathi": title_marathi,
            "title_english": title_english,
            "published_date": pub_date,
            "source_name": source_name,
            "source_url": source_url,
            "article_url": link
        })

    print("\n" + "="*60)
    return news_list


if __name__ == "__main__":
    get_latest_agriculture_news_maharashtra(limit=10, translate_to_english=True)
