import feedparser

RSS_URL = "https://news.google.com/rss/search?q=haridwar+OR+dehradun+OR+uttarakhand&hl=en-IN&gl=IN&ceid=IN:en"


def get_news():
    feed = feedparser.parse(RSS_URL)
    news = []
    for e in feed.entries[:10]:
        news.append({"title": e.title, "link": e.link})
    return news
