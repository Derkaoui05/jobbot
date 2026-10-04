import re, requests, feedparser
from bs4 import BeautifulSoup
UA = {"User-Agent": "jobbot/1.0 (personal job search)"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

def clean(html):
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)

def job(source, title, company, location, url, desc):
    d = clean(desc)
    m = EMAIL.search(d)
    return dict(source=source, title=title or "", company=company or "", location=location or "",
                url=url or "", description=d[:6000], contact_email=m.group(0) if m else "")

def remoteok():
    r = requests.get("https://remoteok.com/api", headers=UA, timeout=30).json()
    for x in r[1:]:  # first item is legal notice
        yield job("remoteok", x.get("position"), x.get("company"), x.get("location") or "Remote",
                  x.get("url"), x.get("description"))

def remotive():
    for q in ("react", "laravel", "full stack", "wordpress", "java"):
        r = requests.get("https://remotive.com/api/remote-jobs", params={"search": q, "limit": 50},
                         headers=UA, timeout=30).json()
        for x in r.get("jobs", []):
            yield job("remotive", x["title"], x["company_name"], x.get("candidate_required_location"),
                      x["url"], x.get("description"))

def weworkremotely():
    for feed in ("remote-full-stack-programming-jobs", "remote-front-end-programming-jobs",
                 "remote-back-end-programming-jobs"):
        f = feedparser.parse(f"https://weworkremotely.com/categories/{feed}.rss")
        for e in f.entries:
            title = e.get("title", "")
            company, _, t = title.partition(": ")
            yield job("weworkremotely", t or title, company if t else "", "Remote", e.get("link"), e.get("summary"))

def arbeitnow():
    r = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=UA, timeout=30).json()
    for x in r.get("data", []):
        yield job("arbeitnow", x["title"], x["company_name"],
                  ("Remote, " if x.get("remote") else "") + (x.get("location") or ""), x["url"], x.get("description"))

def emploi_ma():
    # Best-effort generic extraction; verify robots.txt/terms and adjust before enabling.
    for q in ("developpeur", "react", "laravel", "stage developpeur"):
        html = requests.get("https://www.emploi.ma/recherche-jobs-maroc", params={"keyword": q},
                            headers=UA, timeout=30).text
        for card in BeautifulSoup(html, "html.parser").select("div.card-job, article"):
            a = card.find("a", href=True)
            if a:
                href = a["href"] if a["href"].startswith("http") else "https://www.emploi.ma" + a["href"]
                yield job("emploi_ma", a.get_text(strip=True), "", "Maroc", href, card.get_text(" ", strip=True))

def rekrute():
    for q in ("developpeur", "react", "laravel", "stage"):
        html = requests.get("https://www.rekrute.com/offres.html", params={"keyword": q},
                            headers=UA, timeout=30).text
        for li in BeautifulSoup(html, "html.parser").select("li.post-id, div.section"):
            a = li.find("a", href=True)
            if a and "offre" in a["href"]:
                href = a["href"] if a["href"].startswith("http") else "https://www.rekrute.com" + a["href"]
                yield job("rekrute", a.get_text(strip=True), "", "Maroc", href, li.get_text(" ", strip=True))

REGISTRY = dict(remoteok=remoteok, remotive=remotive, weworkremotely=weworkremotely,
                arbeitnow=arbeitnow, emploi_ma=emploi_ma, rekrute=rekrute)
