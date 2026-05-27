"""
Test-Threads und Kommentare für r/Technologie einfügen.
Ausführen mit: python seed_threads.py
"""
from supabase import create_client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import os

load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

# ── Test-User erstellen ──────────────────────────────────────────────────────
print("Erstelle Test-User...")
users_data = [
    {"username": "jonas_dev",       "email": "jonas_dev@test.ch",       "password_hash": generate_password_hash("test1234")},
    {"username": "naeljörg",        "email": "nael@test.ch",             "password_hash": generate_password_hash("test1234")},
    {"username": "tech_enthusiast", "email": "tech@test.ch",             "password_hash": generate_password_hash("test1234")},
]

user_ids = {}
for u in users_data:
    try:
        res = sb.table("users").upsert(u, on_conflict="email").execute()
        uid = res.data[0]["id"]
        user_ids[u["username"]] = uid
        print(f"  OK {u['username']} ({uid[:8]}...)")
    except Exception as e:
        # Falls schon da, ID per select holen
        res = sb.table("users").select("id").eq("email", u["email"]).execute()
        if res.data:
            uid = res.data[0]["id"]
            user_ids[u["username"]] = uid
            print(f"  bereits vorhanden: {u['username']}")
        else:
            print(f"  FEHLER {u['username']}: {e}")

# ── Technologie-Subreddit ID holen ───────────────────────────────────────────
sub = sb.table("subreddits").select("id").eq("name", "Technologie").execute()
sub_id = sub.data[0]["id"]
print(f"\nSubreddit r/Technologie: {sub_id[:8]}...")

# ── Threads erstellen ────────────────────────────────────────────────────────
print("\nErstelle Threads...")
threads = [
    {
        "title": "Vue.js 4 Release – Was ändert sich für Entwickler?",
        "content": "Vue 4 wurde letzte Woche offiziell angekündigt. Die grössten Änderungen betreffen die Composition API, den neuen Vapor-Mode für bessere Performance und eine überarbeitete Reactivity-Engine. Habt ihr euch schon damit beschäftigt? Lohnt sich eine Migration von Vue 3?",
        "user_id": user_ids.get("jonas_dev"),
        "subreddit_id": sub_id,
    },
    {
        "title": "Welches KI-Tool nutzt ihr täglich? Meine Top 3",
        "content": "Nach einem Jahr Ausprobieren sind das meine drei wichtigsten KI-Tools:\n\n1. Claude – für Code-Reviews und komplexe Texte\n2. Cursor – IDE mit KI direkt integriert\n3. Perplexity – als Suchmaschinen-Ersatz\n\nWas nutzt ihr so?",
        "user_id": user_ids.get("tech_enthusiast"),
        "subreddit_id": sub_id,
    },
    {
        "title": "Ich habe mein erstes Open-Source-Projekt veröffentlicht",
        "content": "Nach 3 Monaten Arbeit habe ich endlich mein erstes Open-Source-Projekt auf GitHub gestellt – eine kleine CLI-Tool zum automatischen Umbenennen von Dateien nach bestimmten Mustern. Feedback sehr willkommen! Link folgt in den Kommentaren.",
        "user_id": user_ids.get("naeljörg"),
        "subreddit_id": sub_id,
    },
    {
        "title": "Python vs. JavaScript – welche Sprache für Anfänger 2025?",
        "content": "Mein jüngerer Bruder (15) will programmieren lernen. Ich bin hin- und hergerissen zwischen Python (einfachere Syntax, Data Science) und JavaScript (direkt im Browser, mehr Feedback). Was würdet ihr empfehlen?",
        "user_id": user_ids.get("jonas_dev"),
        "subreddit_id": sub_id,
    },
]

thread_ids = []
for t in threads:
    try:
        res = sb.table("threads").insert(t).execute()
        tid = res.data[0]["id"]
        thread_ids.append(tid)
        print(f"  OK \"{t['title'][:50]}...\"")
    except Exception as e:
        print(f"  FEHLER: {e}")

# ── Kommentare erstellen ─────────────────────────────────────────────────────
print("\nErstelle Kommentare...")
comments = []

if len(thread_ids) >= 1:
    comments += [
        {"content": "Super interessant! Der Vapor-Mode klingt vielversprechend – hab mal einen Benchmark gesehen, angeblich 2x schneller als Vue 3.", "user_id": user_ids.get("tech_enthusiast"), "thread_id": thread_ids[0]},
        {"content": "Ich bleibe vorerst bei Vue 3. Migration klingt aufwändig und wir haben kaum Zeit dafür. Ausserdem ist Vue 3 noch super supported.", "user_id": user_ids.get("naeljörg"), "thread_id": thread_ids[0]},
        {"content": "Danke für den Überblick! Genau das habe ich gesucht. Die neue Reactivity-Engine würde uns bei unserem Projekt wirklich helfen.", "user_id": user_ids.get("jonas_dev"), "thread_id": thread_ids[0]},
    ]

if len(thread_ids) >= 2:
    comments += [
        {"content": "Ich nutze auch Claude täglich, hauptsächlich für Dokumentation und Code-Erklärungen. Cursor habe ich noch nicht ausprobiert – wie ist die Integration mit bestehenden Projekten?", "user_id": user_ids.get("naeljörg"), "thread_id": thread_ids[1]},
        {"content": "GitHub Copilot fehlt auf deiner Liste! Direkt im Editor, sehr praktisch. Aber Claude für komplexere Sachen stimmt, da ist er deutlich besser.", "user_id": user_ids.get("jonas_dev"), "thread_id": thread_ids[1]},
    ]

if len(thread_ids) >= 3:
    comments += [
        {"content": "Herzlichen Glückwunsch zum ersten Open-Source-Projekt! Hast du schon überlegt, Tests zu schreiben? Das würde den Einstieg für Contributors erleichtern.", "user_id": user_ids.get("tech_enthusiast"), "thread_id": thread_ids[2]},
        {"content": "Sehr cool! Ich schaue mir das gerne an. Hast du es auf PyPI hochgeladen?", "user_id": user_ids.get("jonas_dev"), "thread_id": thread_ids[2]},
        {"content": "Super Projekt! Ich hatte letztens das gleiche Problem mit Datei-Umbenennung. Werde auf jeden Fall reinschauen.", "user_id": user_ids.get("naeljörg"), "thread_id": thread_ids[2]},
    ]

if len(thread_ids) >= 4:
    comments += [
        {"content": "Definitiv Python für Anfänger! Ich habe selbst mit Python angefangen und die Syntax ist so viel lesbarer. Man kann sich auf die Konzepte konzentrieren statt auf Semikolons.", "user_id": user_ids.get("tech_enthusiast"), "thread_id": thread_ids[3]},
        {"content": "JavaScript hätte den Vorteil, dass man direkt im Browser Ergebnisse sieht. Für einen 15-Jährigen ist das motivierender. Ich würde JS empfehlen.", "user_id": user_ids.get("naeljörg"), "thread_id": thread_ids[3]},
    ]

for c in comments:
    try:
        sb.table("comments").insert(c).execute()
        print(f"  OK Kommentar von {next(k for k,v in user_ids.items() if v == c['user_id'])}")
    except Exception as e:
        print(f"  FEHLER: {e}")

print("\nFertig! Seite neu laden um alles zu sehen.")
