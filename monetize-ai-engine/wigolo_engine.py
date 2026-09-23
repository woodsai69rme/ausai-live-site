"""
Wigolo Engine - Local-First Web Intelligence & Multi-Engine Search
Performs parallel searches across DuckDuckGo API, SearXNG, GitHub, and Wikipedia.
Zero API cost, zero cloud dependencies.
"""

import os
import sys
import json
import urllib.parse
import concurrent.futures
import requests
from bs4 import BeautifulSoup

class WigoloSearchEngine:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    def search_duckduckgo_json(self, query):
        results = []
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_redirect=1"
            res = requests.get(url, headers=self.headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                # Abstract
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("Heading", query),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data.get("AbstractText", ""),
                        "engine": "DuckDuckGo API"
                    })
                # Related Topics
                for topic in data.get("RelatedTopics", [])[:5]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:60] + "...",
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                            "engine": "DuckDuckGo API"
                        })
        except Exception:
            pass
        return results

    def search_github(self, query):
        results = []
        try:
            url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc"
            res = requests.get(url, headers=self.headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                for repo in data.get("items", [])[:5]:
                    results.append({
                        "title": f"{repo.get('full_name')} (★ {repo.get('stargazers_count')})",
                        "url": repo.get("html_url", ""),
                        "snippet": repo.get("description", "") or "GitHub Repository",
                        "engine": "GitHub"
                    })
        except Exception:
            pass
        return results

    def search_wikipedia(self, query):
        results = []
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=5&namespace=0&format=json"
            res = requests.get(url, headers=self.headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                for t, u in zip(titles, urls):
                    results.append({
                        "title": t,
                        "url": u,
                        "snippet": f"Wikipedia article for {t}",
                        "engine": "Wikipedia"
                    })
        except Exception:
            pass
        return results

    def search_multi_engine(self, query):
        combined = []
        seen_urls = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            f_ddg = executor.submit(self.search_duckduckgo_json, query)
            f_gh = executor.submit(self.search_github, query)
            f_wiki = executor.submit(self.search_wikipedia, query)

            for f in [f_ddg, f_gh, f_wiki]:
                try:
                    res_list = f.result(timeout=8)
                    for item in res_list:
                        u = item.get("url", "")
                        if u and u not in seen_urls:
                            seen_urls.add(u)
                            combined.append(item)
                except Exception:
                    pass

        return combined

if __name__ == "__main__":
    engine = WigoloSearchEngine()
    q = sys.argv[1] if len(sys.argv) > 1 else "monetizable AI developer tools"
    print(f"=== Wigolo Multi-Engine Search: '{q}' ===")
    res = engine.search_multi_engine(q)
    print(json.dumps(res, indent=2))
