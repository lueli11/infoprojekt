"""
Testdaten für Temu Reddit einfügen.
Ausführen mit: python seed_data.py
"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ── Subreddits ──────────────────────────────────────────────────────────────
communities = [
    {"name": "Technologie",  "description": "Alles rund um Tech, Code, KI und Gadgets"},
    {"name": "Schweiz",      "description": "News, Kultur und Diskussionen aus der Schweiz 🇨🇭"},
    {"name": "Gaming",       "description": "Spiele, Reviews und Community-Challenges"},
    {"name": "Musik",        "description": "Neue Releases, Konzerte und alles über Musik"},
    {"name": "Allgemein",    "description": "Für alles, was sonst nirgends passt"},
]

print("Füge Subreddits ein...")
for c in communities:
    try:
        supabase.table("subreddits").upsert(c, on_conflict="name").execute()
        print(f"  OK r/{c['name']}")
    except Exception as e:
        print(f"  FEHLER r/{c['name']}: {e}")

print("\nFertig!")
