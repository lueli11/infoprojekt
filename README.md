# Temu Reddit

Eine Reddit-ähnliche Community-Plattform als Schulprojekt.  
Benutzer können Subreddits durchsuchen, Threads erstellen und kommentieren.

## Tech-Stack

| Schicht | Technologie |
|---|---|
| Frontend | Vue.js 3 (CDN, kein Build-Step) · Vanilla CSS |
| Backend | Python 3 · Flask · Flask-JWT-Extended |
| Datenbank | Supabase (PostgreSQL) |
| Deployment | Docker · Gunicorn · Coolify |

---

## Projektstruktur

```
infoprojekt/
├── main.html          # Gesamtes Frontend (Vue.js SPA)
├── app.py             # Flask REST-API
├── requirements.txt   # Python-Abhängigkeiten
├── Dockerfile         # Produktions-Container
├── Procfile           # Heroku-Kompatibilität
├── .env               # Secrets (NICHT im Git)
├── .dockerignore      # Schließt Secrets aus dem Image aus
├── seed_data.py       # Test-Subreddits einfügen
├── seed_threads.py    # Test-Threads & Kommentare einfügen
├── setup_db.py        # DB-Tabellen erstellen (direkter PG-Zugriff)
└── ideen/             # Design-Mockups (HTML-Prototypen)
```

---

## Lokale Entwicklung

### Voraussetzungen
- Python 3.10+
- Supabase-Projekt (kostenlos unter [supabase.com](https://supabase.com))

### 1. Repository klonen & Abhängigkeiten installieren

```bash
git clone <repo-url>
cd infoprojekt
pip install -r requirements.txt
```

### 2. `.env` erstellen

```env
SUPABASE_URL=https://<dein-projekt>.supabase.co
SUPABASE_KEY=<dein-anon-key>
SUPABASE_DB_PASSWORD=<dein-db-passwort>
JWT_SECRET_KEY=<beliebiger-geheimer-string>
```

### 3. Datenbank einrichten

Im [Supabase SQL-Editor](https://supabase.com/dashboard) folgendes SQL ausführen:

```sql
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  description TEXT,
  pfp TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subreddits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  logo TEXT,
  banner TEXT,
  creator_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  user_id UUID REFERENCES users(id),
  subreddit_id UUID REFERENCES subreddits(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  user_id UUID REFERENCES users(id),
  thread_id UUID REFERENCES threads(id),
  reply_id UUID REFERENCES comments(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Row Level Security deaktivieren (Entwicklungsmodus)
ALTER TABLE users     DISABLE ROW LEVEL SECURITY;
ALTER TABLE subreddits DISABLE ROW LEVEL SECURITY;
ALTER TABLE threads   DISABLE ROW LEVEL SECURITY;
ALTER TABLE comments  DISABLE ROW LEVEL SECURITY;
```

### 4. Server starten

```bash
python app.py
# → http://localhost:8080
```

### 5. (Optional) Testdaten einfügen

```bash
python seed_data.py      # 5 Test-Subreddits
python seed_threads.py   # Threads + Kommentare in r/Technologie
                         # Test-Login: jonas_dev@test.ch / test1234
```

---

## API-Referenz

Alle Endpunkte beginnen mit dem Server-Basis-URL (lokal: `http://localhost:8080`).

| Methode | Pfad | Auth | Beschreibung |
|---|---|---|---|
| `POST` | `/users/register` | – | Neuen Benutzer registrieren |
| `POST` | `/auth/login` | – | Login, gibt JWT-Token zurück |
| `GET` | `/users/<id>` | – | Benutzerprofil abrufen |
| `GET` | `/subreddits` | – | Alle Subreddits auflisten |
| `POST` | `/subreddits` | ✅ JWT | Neuen Subreddit erstellen |
| `GET` | `/subreddits/<id>` | – | Subreddit-Details |
| `GET` | `/subreddits/<id>/threads` | – | Threads eines Subreddits |
| `GET` | `/threads` | – | Alle Threads (neueste zuerst) |
| `POST` | `/threads` | ✅ JWT | Neuen Thread erstellen |
| `GET` | `/threads/<id>` | – | Thread-Details mit User & Subreddit |
| `GET` | `/threads/<id>/comments` | – | Kommentare eines Threads |
| `POST` | `/threads/<id>/comments` | ✅ JWT | Kommentar schreiben |

**Auth-Header für geschützte Endpunkte:**
```
Authorization: Bearer <jwt-token>
```

---

## Frontend-Architektur

Das gesamte Frontend befindet sich in **einer einzigen Datei** (`main.html`) — keine Build-Tools, kein npm.

```
Vue-App (#app)
├── Navbar (sticky, immer sichtbar)
│   ├── Logo → Home
│   ├── Breadcrumb (Home > r/Subreddit > Thread)
│   └── Register|Login Button / User-Chip + Abmelden
│
├── Auth-Modal (v-if showAuthModal)
│   ├── Tab: Anmelden
│   └── Tab: Registrieren
│
├── Home-View (v-if currentView === 'home')
│   └── Subreddit-Grid (Karten, klickbar)
│
├── Subreddit-View (v-if currentView === 'subreddit')
│   ├── Banner + Header
│   ├── "Neuer Thread"-Formular (nur eingeloggt)
│   └── Thread-Liste (klickbar)
│
└── Thread-View (v-if currentView === 'thread')
    ├── Original-Post
    ├── Kommentar-Eingabe (nur eingeloggt)
    └── Kommentar-Liste
```

**State-Management:**
- Navigation via `currentView` String (`'home'` | `'subreddit'` | `'thread'`)
- JWT + User in `localStorage` gespeichert (bleibt nach Reload)
- API-Base-URL: automatisch relativ in Produktion, `http://localhost:8080` lokal

---

## Deployment mit Coolify

### Voraussetzungen
- Laufende Coolify-Instanz (self-hosted)
- Git-Repository (GitHub, GitLab, etc.)
- Supabase-Projekt mit erstellten Tabellen (s.o.)

### Schritte

**1. Neues Projekt anlegen**  
Coolify Dashboard → *New Project* → *Add Resource* → *Git Repository*

**2. Repository verbinden**  
- Repository-URL eintragen
- Branch: `main`
- Build Pack: **Dockerfile** auswählen

**3. Port konfigurieren**  
Port: `3011` (steht im Dockerfile)

**4. Environment Variables setzen**  
> ⚠️ Die `.env`-Datei wird **nicht** ins Docker-Image kopiert (via `.dockerignore`). Secrets **müssen** hier eingetragen werden.

| Variable | Wert |
|---|---|
| `SUPABASE_URL` | `https://<projekt-id>.supabase.co` |
| `SUPABASE_KEY` | Anon/Publishable Key aus Supabase |
| `JWT_SECRET_KEY` | Beliebiger sicherer String (mind. 32 Zeichen) |

**5. Deploy**  
*Deploy* klicken — Coolify baut das Docker-Image und startet den Container.  
Danach ist die App unter der konfigurierten Domain/IP erreichbar.

### Wie funktioniert das Deployment?

```
Coolify
└── Docker-Container
    ├── gunicorn (WSGI-Server, Port 3011)
    └── Flask-App (app.py)
        ├── GET /          → liefert main.html aus
        ├── GET /subreddits → API
        └── ...weitere API-Endpunkte
```

Der Container serviert **alles** — Frontend und Backend laufen im selben Prozess. Kein separater Web-Server (nginx etc.) nötig.

---

## Datenbank-Schema

```
users
  id UUID PK │ username TEXT UNIQUE │ email TEXT UNIQUE
  password_hash TEXT │ description TEXT │ pfp TEXT │ created_at

subreddits
  id UUID PK │ name TEXT UNIQUE │ description TEXT
  logo TEXT │ banner TEXT │ creator_id → users.id │ created_at

threads
  id UUID PK │ title TEXT │ content TEXT
  user_id → users.id │ subreddit_id → subreddits.id │ created_at

comments
  id UUID PK │ content TEXT
  user_id → users.id │ thread_id → threads.id
  reply_id → comments.id (für Antworten) │ created_at
```

---

## Bewusst nicht implementiert

- Voting / Upvotes
- Subreddit erstellen via UI (nur über API möglich)
- Nested Replies (Datenmodell vorhanden, UI fehlt)
- Bildupload
- Suchfunktion
- User-Profilseiten
