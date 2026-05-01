from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret-bitte-aendern")
jwt = JWTManager(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── AUTH ────────────────────────────────────────────────────────────────────

@app.route("/users/register", methods=["POST"])
def register():
    daten = request.get_json()
    username = daten.get("username")
    email    = daten.get("email")
    password = daten.get("password")

    if not username or not email or not password:
        return jsonify({"fehler": "username, email und password sind Pflicht"}), 400

    passwort_hash = generate_password_hash(password)

    result = supabase.table("users").insert({
        "username": username,
        "email": email,
        "password_hash": passwort_hash,
    }).execute()

    user = result.data[0]
    return jsonify({"id": user["id"], "username": user["username"]}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    daten = request.get_json()
    email    = daten.get("email")
    password = daten.get("password")

    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        return jsonify({"fehler": "Ungültige Anmeldedaten"}), 401

    user = result.data[0]
    if not check_password_hash(user["password_hash"], password):
        return jsonify({"fehler": "Ungültige Anmeldedaten"}), 401

    token = create_access_token(identity=user["id"])
    return jsonify({"token": token, "user_id": user["id"], "username": user["username"]})


# ── USERS ────────────────────────────────────────────────────────────────────

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    result = supabase.table("users").select("id, username, description, pfp").eq("id", user_id).execute()
    if not result.data:
        return jsonify({"fehler": "Benutzer nicht gefunden"}), 404
    return jsonify(result.data[0])


# ── SUBREDDITS ───────────────────────────────────────────────────────────────

@app.route("/subreddits", methods=["GET"])
def get_subreddits():
    result = supabase.table("subreddits").select("*").execute()
    return jsonify(result.data)


@app.route("/subreddits", methods=["POST"])
@jwt_required()
def create_subreddit():
    user_id = get_jwt_identity()
    daten = request.get_json()
    name        = daten.get("name")
    description = daten.get("description", "")

    if not name:
        return jsonify({"fehler": "name ist Pflicht"}), 400

    result = supabase.table("subreddits").insert({
        "name": name,
        "description": description,
        "creator_id": user_id,
    }).execute()

    return jsonify(result.data[0]), 201


@app.route("/subreddits/<subreddit_id>", methods=["GET"])
def get_subreddit(subreddit_id):
    result = supabase.table("subreddits").select("*").eq("id", subreddit_id).execute()
    if not result.data:
        return jsonify({"fehler": "Subreddit nicht gefunden"}), 404
    return jsonify(result.data[0])


@app.route("/subreddits/<subreddit_id>/threads", methods=["GET"])
def get_threads_by_subreddit(subreddit_id):
    result = (
        supabase.table("threads")
        .select("*, users(username)")
        .eq("subreddit_id", subreddit_id)
        .order("created_at", desc=True)
        .execute()
    )
    return jsonify(result.data)


# ── THREADS ──────────────────────────────────────────────────────────────────

@app.route("/threads", methods=["POST"])
@jwt_required()
def create_thread():
    user_id = get_jwt_identity()
    daten = request.get_json()
    title        = daten.get("title")
    content      = daten.get("content", "")
    subreddit_id = daten.get("subreddit_id")

    if not title or not subreddit_id:
        return jsonify({"fehler": "title und subreddit_id sind Pflicht"}), 400

    result = supabase.table("threads").insert({
        "title": title,
        "content": content,
        "user_id": user_id,
        "subreddit_id": subreddit_id,
    }).execute()

    return jsonify(result.data[0]), 201


@app.route("/threads/<thread_id>", methods=["GET"])
def get_thread(thread_id):
    result = (
        supabase.table("threads")
        .select("*, users(username), subreddits(name)")
        .eq("id", thread_id)
        .execute()
    )
    if not result.data:
        return jsonify({"fehler": "Thread nicht gefunden"}), 404
    return jsonify(result.data[0])


# ── KOMMENTARE ───────────────────────────────────────────────────────────────

@app.route("/threads/<thread_id>/comments", methods=["GET"])
def get_comments(thread_id):
    result = (
        supabase.table("comments")
        .select("*, users(username)")
        .eq("thread_id", thread_id)
        .order("created_at")
        .execute()
    )
    return jsonify(result.data)


@app.route("/threads/<thread_id>/comments", methods=["POST"])
@jwt_required()
def create_comment(thread_id):
    user_id = get_jwt_identity()
    daten = request.get_json()
    content = daten.get("content")

    if not content:
        return jsonify({"fehler": "content ist Pflicht"}), 400

    result = supabase.table("comments").insert({
        "content": content,
        "user_id": user_id,
        "thread_id": thread_id,
    }).execute()

    return jsonify(result.data[0]), 201


if __name__ == "__main__":
    app.run(debug=True)

pw von supabase nicht löschen!!!: mcwlZMuWbeFb1zXD