import requests
from bs4 import BeautifulSoup

def collect_github_trends():
    url = "https://github.com/trending"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    repos = soup.find_all("article")

    results = []

    for repo in repos[:10]:
        title = repo.h2.text.strip().replace("\n", "").replace(" ", "")
        
        results.append({
            "repo": title
        })

    return results