import os, json, anthropic
MODEL = os.getenv("JOBBOT_MODEL", "claude-sonnet-5-5")

def make_letter(j, cfg, lang):
    client = anthropic.Anthropic()
    prompt = f"""Write a concise job application email/cover letter ({'in French' if lang=='fr' else 'in English'}), 150-220 words.
STRICT RULES: use ONLY facts from the PROFILE below. Never invent employers, years of experience, degrees, metrics or skills.
If the offer asks for something not in the profile, do not claim it. Be specific about which parts of the offer match the profile.
Start with a subject line ("Objet:" / "Subject:"). Sign with the candidate's name, portfolio and email.

PROFILE:
{json.dumps(cfg['profile'], ensure_ascii=False, indent=1)}

OFFER:
Title: {j['title']}
Company: {j['company']}
Location: {j['location']}
Description: {j['description'][:3500]}"""
    r = client.messages.create(model=MODEL, max_tokens=700, messages=[{"role": "user", "content": prompt}])
    return r.content[0].text.strip()
