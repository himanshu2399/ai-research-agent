import feedparser

feeds = [
    "https://aws.amazon.com/blogs/devops/feed/",
    "https://cloud.google.com/blog/topics/developers-practitioners/rss/",
    "https://kubernetes.io/feed.xml",
    "https://www.cncf.io/feed/"
]

def collect_rss_articles():
    articles = []

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link
            })

    return articles