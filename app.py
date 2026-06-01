from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")
jwt = JWTManager(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── FRONTEND Ai gemacht dass wir Seiten reloaden konnte zum testen und zu domain wechseln konnten

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/r/<path:path>")
def serve_r(path):
    return send_from_directory(".", "index.html")

# ── AUTH eben auch von AI

@app.route("/users/register", methods=["POST"])
def register():
    daten = request.get_json()
    username = daten.get("username")
    email    = daten.get("email")
    password = daten.get("password")

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
    user = result.data[0]

    token = create_access_token(identity=user["id"])
    return jsonify({"token": token, "user_id": user["id"], "username": user["username"]})


# ── SUBREDDITS 

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

    result = supabase.table("subreddits").insert({
        "name": name,
        "description": description,
        "creator_id": user_id,
    }).execute()

    return jsonify({"ok": True}), 201


@app.route("/subreddits/<subreddit_id>", methods=["DELETE"])
@jwt_required()
def delete_subreddit(subreddit_id):
    supabase.table("subreddits").delete().eq("id", subreddit_id).execute()
    return jsonify({"ok": True})


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


# ── THREADS 

@app.route("/threads", methods=["POST"])
@jwt_required()
def create_thread():
    user_id = get_jwt_identity()
    daten = request.get_json()
    title        = daten.get("title")
    content      = daten.get("content", "")
    subreddit_id = daten.get("subreddit_id")

    result = supabase.table("threads").insert({
        "title": title,
        "content": content,
        "user_id": user_id,
        "subreddit_id": subreddit_id,
    }).execute()

    return jsonify({"ok": True}), 201


@app.route("/threads/<thread_id>", methods=["DELETE"])
@jwt_required()
def delete_thread(thread_id):
    supabase.table("threads").delete().eq("id", thread_id).execute()
    return jsonify({"ok": True})


@app.route("/threads/<thread_id>", methods=["GET"])
def get_thread(thread_id):
    result = (
        supabase.table("threads")
        .select("*, users(username), subreddits(name)")
        .eq("id", thread_id)
        .execute()
    )
    return jsonify(result.data[0])


# ── Comments 

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


@app.route("/comments/<comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    supabase.table("comments").delete().eq("id", comment_id).execute()
    return jsonify({"ok": True})


@app.route("/threads/<thread_id>/comments", methods=["POST"])
@jwt_required()
def create_comment(thread_id):
    user_id = get_jwt_identity()
    daten = request.get_json()
    content = daten.get("content")

    result = supabase.table("comments").insert({
        "content": content,
        "user_id": user_id,
        "thread_id": thread_id,
        "reply_id": daten.get("reply_id"),
    }).execute()

    return jsonify({"ok": True}), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3011))
    app.run(debug=True, port=port)