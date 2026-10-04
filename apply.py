import os, smtplib, mimetypes
from email.message import EmailMessage

def send_application(j, cfg, cv_path="cv.pdf"):
    """Sends ONLY to an email address found in the offer, and only for approved jobs."""
    if not j["contact_email"]:
        raise ValueError("No contact email in this offer: apply manually via " + j["url"])
    lines = j["letter"].splitlines()
    subject = lines[0].split(":", 1)[-1].strip() if lines and ":" in lines[0] else f"Candidature - {j['title']}"
    body = "\n".join(lines[1:]).strip() if lines and ":" in lines[0] else j["letter"]
    m = EmailMessage()
    m["From"], m["To"], m["Subject"] = os.environ["SMTP_USER"], j["contact_email"], subject
    m.set_content(body)
    if os.path.exists(cv_path):
        ctype = mimetypes.guess_type(cv_path)[0] or "application/pdf"
        m.add_attachment(open(cv_path, "rb").read(), maintype=ctype.split("/")[0],
                         subtype=ctype.split("/")[1], filename=os.path.basename(cv_path))
    with smtplib.SMTP_SSL(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", 465))) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])  # Gmail: use an App Password
        s.send_message(m)
