# jobbot

Collect offers -> score vs your profile -> tailored letters -> daily Telegram digest -> you approve -> email sent.

## Setup (5 min)
1. `pip install -r requirements.txt`
2. Edit `config.yaml` (your email, skills, min_score). Put your CV at `cv.pdf`.
3. Env vars:
   - `ANTHROPIC_API_KEY` (letters)
   - `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` (optional; otherwise the digest prints to console)
   - `SMTP_USER`, `SMTP_PASS` (Gmail App Password), optional `SMTP_HOST`, `SMTP_PORT`
4. `python main.py run`

## Daily use
    python main.py list            # digested matches
    python main.py show 12         # read offer + letter, edit if you want
    python main.py approve 12
    python main.py send            # emails approved offers that list a contact address
    python main.py done 12         # you applied manually via the website

Offers without a contact email are never auto-sent: open the URL and paste the letter.

## Schedule
- Local: cron `0 8 * * * cd /path/jobbot && python main.py run`
- Or GitHub Actions (`.github/workflows/jobbot.yml`) in a PRIVATE repo; add the secrets there.

## Notes
- LinkedIn/Indeed are deliberately not scraped (ToS; account bans).
- `emploi_ma` and `rekrute` are best-effort HTML adapters, disabled by default: check each site's
  terms/robots.txt and fix the selectors against the live page before enabling.
- Always read the letter before approving; the generator is told to use only your profile facts.
