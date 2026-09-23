import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "blog-secret-key-change-in-production"

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts.json")


def load_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


@app.route("/")
def index():
    posts = load_posts()
    posts_sorted = sorted(posts, key=lambda p: p["created_at"], reverse=True)
    return render_template("index.html", posts=posts_sorted)


@app.route("/post/<post_id>")
def view_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        flash("Post not found.", "error")
        return redirect(url_for("index"))
    return render_template("post.html", post=post)


@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not author or not content:
            flash("All fields are required.", "error")
            return render_template("new.html", title=title, author=author, content=content)

        posts = load_posts()
        post = {
            "id": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "content": content,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        posts.append(post)
        save_posts(posts)
        flash("Post created successfully!", "success")
        return redirect(url_for("view_post", post_id=post["id"]))

    return render_template("new.html")


@app.route("/edit/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        flash("Post not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not author or not content:
            flash("All fields are required.", "error")
            return render_template("edit.html", post=post)

        post["title"] = title
        post["author"] = author
        post["content"] = content
        post["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_posts(posts)
        flash("Post updated successfully!", "success")
        return redirect(url_for("view_post", post_id=post["id"]))

    return render_template("edit.html", post=post)


@app.route("/delete/<post_id>", methods=["POST"])
def delete_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        flash("Post not found.", "error")
        return redirect(url_for("index"))

    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    flash("Post deleted.", "success")
    return redirect(url_for("index"))


def format_date(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except (ValueError, TypeError):
        return value


app.jinja_env.filters["format_date"] = format_date


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
