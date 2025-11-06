import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

def get_latest_agriculture_news_maharashtra(limit=15, translate_to_english=False):
    """
    Fetches the latest agriculture news from Maharashtra from Google News RSS (in Marathi).
    Optionally translates titles to English.

    Returns:
        List[dict]: Each dict contains Marathi title, optional English title, date, source, and link.
    """
    try:
        # Marathi keywords for agriculture + Maharashtra
        query = "(कृषी OR शेतकरी OR पिके OR शेती) महाराष्ट्र"
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=mr&gl=IN&ceid=IN:mr"

        # Fetch RSS feed
        resp = requests.get(rss_url, timeout=10)
        if resp.status_code != 200:
            return {"error": f"Failed to fetch news: {resp.status_code}"}

        soup = BeautifulSoup(resp.content, "lxml-xml")
        items = soup.find_all("item")[:limit]
        if not items:
            return {"error": "No news found."}

        news_list = []
        for item in items:
            title_marathi = item.title.text
            link = item.link.text
            pub_date = item.pubDate.text if item.pubDate else "N/A"
            source_tag = item.find("source")
            source_name = source_tag.text if source_tag else "Unknown Source"
            source_url = source_tag["url"] if source_tag and source_tag.has_attr("url") else ""

            # Optional translation to English
            title_english = None
            if translate_to_english:
                try:
                    title_english = GoogleTranslator(source='mr', target='en').translate(title_marathi)
                except Exception:
                    title_english = "Translation error"

            news_list.append({
                "title_marathi": title_marathi,
                "title_english": title_english,
                "published_date": pub_date,
                "source_name": source_name,
                "source_url": source_url,
                "article_url": link
            })

        return news_list

    except Exception as e:
        return {"error": str(e)}


# Optional: direct run testing
if __name__ == "__main__":
    from pprint import pprint
    pprint(get_latest_agriculture_news_maharashtra(limit=5, translate_to_english=True))
