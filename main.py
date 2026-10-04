"""Usage:
  python main.py run             # collect + score + letters + digest (schedule this)
  python main.py list [status]   # show jobs
  python main.py show ID         # show offer + letter
  python main.py approve ID      # mark for sending
  python main.py send            # send approved applications that have a contact email
  python main.py reject ID | done ID   # reject / mark applied manually
"""
import sys, yaml, traceback
import db, sources, scoring, letters, notify, apply

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))

def collect(c):
    new = 0
    for name, opts in cfg["sources"].items():
        if not opts.get("enabled"):
            continue
        try:
            for j in sources.REGISTRY[name]():
                new += db.add(c, j)
        except Exception:
            print(f"[{name}] failed:", traceback.format_exc(limit=1))
    c.commit()
    return new

def run():
    c = db.conn()
    new = collect(c)
    for r in c.execute("SELECT * FROM jobs WHERE status='new'").fetchall():
        c.execute("UPDATE jobs SET score=?, status='scored', lang=? WHERE id=?",
                  (scoring.score(r, cfg), scoring.detect_lang(r["title"] + " " + r["description"]), r["id"]))
    c.commit()
    top = c.execute("SELECT * FROM jobs WHERE status='scored' AND score>=? ORDER BY score DESC LIMIT ?",
                    (cfg["search"]["min_score"], cfg["search"]["max_letters_per_run"])).fetchall()
    out = [f"🔎 {new} new offers, {len(top)} good matches\n"]
    for r in top:
        try:
            letter = letters.make_letter(r, cfg, r["lang"])
        except Exception as e:
            letter = ""; print("letter failed:", e)
        c.execute("UPDATE jobs SET letter=?, status='digested' WHERE id=?", (letter, r["id"]))
        mail = f"\n📧 {r['contact_email']}" if r["contact_email"] else ""
        out.append(f"#{r['id']} [{int(r['score'])}] {r['title']} — {r['company']} ({r['location']})\n{r['url']}{mail}\n")
    c.commit()
    out.append("Review: python main.py show ID | approve ID | send")
    notify.telegram("\n".join(out))

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    c = db.conn()
    if cmd == "run":
        run()
    elif cmd == "list":
        st = sys.argv[2] if len(sys.argv) > 2 else "digested"
        for r in c.execute("SELECT id,score,title,company,status FROM jobs WHERE status=? ORDER BY score DESC", (st,)):
            print(f"#{r['id']} [{int(r['score'])}] {r['title']} - {r['company']} ({r['status']})")
    elif cmd == "show":
        r = c.execute("SELECT * FROM jobs WHERE id=?", (sys.argv[2],)).fetchone()
        print(f"{r['title']} - {r['company']}\n{r['url']}\nContact: {r['contact_email'] or 'none'}\n\n{r['description'][:1500]}\n\n--- LETTER ---\n{r['letter']}")
    elif cmd in ("approve", "reject", "done"):
        st = dict(approve="approved", reject="rejected", done="applied_manual")[cmd]
        c.execute("UPDATE jobs SET status=? WHERE id=?", (st, sys.argv[2])); c.commit(); print("ok")
    elif cmd == "send":
        for r in c.execute("SELECT * FROM jobs WHERE status='approved'").fetchall():
            try:
                apply.send_application(r, cfg); c.execute("UPDATE jobs SET status='sent' WHERE id=?", (r["id"],))
                print("sent", r["id"])
            except Exception as e:
                print(f"#{r['id']} not sent: {e}")
        c.commit()

if __name__ == "__main__":
    main()
