import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="db.woohwgywmwdfgffyatwy.supabase.co",
    port=5432,
    dbname="postgres",
    user="postgres",
    password=os.environ.get("SUPABASE_DB_PASSWORD"),
    sslmode="require"
)
cur = conn.cursor()

sql = """
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
"""

cur.execute(sql)
conn.commit()
cur.close()
conn.close()
print("Alle Tabellen erfolgreich erstellt!")
