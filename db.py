import sqlite3, hashlib, time
DB = "jobs.db"

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT UNIQUE, source TEXT, title TEXT,
        company TEXT, location TEXT, url TEXT, description TEXT, contact_email TEXT,
        score REAL DEFAULT 0, letter TEXT, lang TEXT,
        status TEXT DEFAULT 'new',  -- new | scored | digested | approved | sent | rejected | applied_manual
        created REAL)""")
    return c

def uid(title, company, url):
    return hashlib.sha1(f"{title}|{company}|{url}".lower().encode()).hexdigest()

def add(c, j):
    try:
        c.execute("""INSERT INTO jobs(uid,source,title,company,location,url,description,contact_email,created)
                     VALUES(?,?,?,?,?,?,?,?,?)""",
                  (uid(j["title"], j["company"], j["url"]), j["source"], j["title"], j["company"],
                   j["location"], j["url"], j["description"], j.get("contact_email", ""), time.time()))
        return True
    except sqlite3.IntegrityError:
        return False
