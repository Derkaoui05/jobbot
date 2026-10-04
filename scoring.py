import re

def detect_lang(text):
    fr = len(re.findall(r"\b(nous|vous|poste|expérience|développeur|avec|pour|dans|des|les)\b", text.lower()))
    en = len(re.findall(r"\b(we|you|our|experience|developer|with|for|the|and|team)\b", text.lower()))
    return "fr" if fr > en else "en"

def score(j, cfg):
    s = cfg["search"]
    title = j["title"].lower()
    text = f'{title} {j["description"].lower()} {j["location"].lower()}'
    if any(x in title for x in s["exclude_title"]):
        return 0
    pts = 0
    for kw, w in s["skills"].items():
        if kw in title:
            pts += w * 1.5
        elif kw in text:
            pts += w
    pts = min(pts, 70)
    if any(l in text for l in s["locations_ok"]):
        pts += 20
    else:
        pts -= 25
    # penalise heavy seniority requirements in the body
    if re.search(r"\b([5-9]|1\d)\s*\+?\s*(years|ans)\b", text):
        pts -= 20
    return max(0, min(100, pts))
