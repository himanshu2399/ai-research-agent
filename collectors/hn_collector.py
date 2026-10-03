import requests

def collect_hn_posts():
    url = "https://hn.algolia.com/api/v1/search?tags=front_page"

    response = requests.get(url)

    data = response.json()

    posts = []

    for item in data["hits"][:10]:
        posts.append({
            "title": item.get("title"),
            "url": item.get("url")
        })

    return posts