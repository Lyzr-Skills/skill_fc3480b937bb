#!/usr/bin/env python3
"""Web search via Tavily or Brave. Standard library only.
Usage: search.py "query" [--max N]
Prints JSON list of {title, url, snippet}."""
import argparse, json, os, sys, urllib.parse, urllib.request

def tavily(q, n, key):
    body = json.dumps({"query": q, "max_results": n, "search_depth": "basic"}).encode()
    req = urllib.request.Request("https://api.tavily.com/search", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return [{"title": x.get("title", ""), "url": x.get("url", ""), "snippet": x.get("content", "")}
            for x in data.get("results", [])]

def brave(q, n, key):
    url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode({"q": q, "count": n})
    req = urllib.request.Request(url, headers={"Accept": "application/json", "X-Subscription-Token": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return [{"title": x.get("title", ""), "url": x.get("url", ""), "snippet": x.get("description", "")}
            for x in data.get("web", {}).get("results", [])]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--max", type=int, default=5)
    a = p.parse_args()
    n = max(1, min(a.max, 10))
    try:
        if os.environ.get("TAVILY_API_KEY"):
            res = tavily(a.query, n, os.environ["TAVILY_API_KEY"])
        elif os.environ.get("BRAVE_API_KEY"):
            res = brave(a.query, n, os.environ["BRAVE_API_KEY"])
        else:
            print(json.dumps({"error": "No search API key. Set TAVILY_API_KEY or BRAVE_API_KEY."}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Search failed: {e}"}))
        sys.exit(1)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
