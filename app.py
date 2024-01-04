"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ihaveasecret'
app.app_context().push()

connect_db(app)
db.create_all()

@app.route('/')
def root():
    """Show recent list of posts, most-recent first."""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404

@app.route('/users')
def load_users():
    """Loads user list"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)

@app.route('/users/new', methods=["GET"])
def add_user_form():
    """Shows form to add new user"""

    return render_template("users/new.html")

@app.route('/users/new', methods=["POST"])
def add_user():
    new_user=User(
        first_name = request.form['first_name'],
        last_name = request.form['last_name'],
        image_url = request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)

@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>/posts/new')
def add_post_form(user_id):
    """Shows form for user to add new post"""

    user=User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('posts/new.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def handle_post_form(user_id):
    """Handles new post form submission"""

    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    new_post = Post(title = request.form["title"], content = request.form["content"], user=user, tags=tags)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added")

    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Shows page with a specific post"""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def show_edit_form(post_id):
    """Show form to edit a post"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template("posts/edit.html", post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def handle_edit_form(post_id):
    """Handles form submission to edit a post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' edited.")

    return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Deletes post"""
    
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted.")

    return redirect(f"/users/{post.user_id}")

# Need a Show Tag route, listing the available tags and including a link to the Create Tag page
@app.route('/tags')
def show_all_tags():
    """Shows all available tags"""

    tags = Tag.query.all()
    return render_template("/tags/index.html", tags=tags)

# Need a Create Tag route, both a GET to show the form, and a POST to add entered tag into 'tags' table
@app.route('/tags/new')
def add_tag_form():
    """Shows form to create new tag"""

    posts = Post.query.all()
    return render_template("tags/new.html", posts=posts)

@app.route('/tags/new', methods=["POST"])
def handle_tag_form():
    """Handles form submission to create new tag"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag=Tag(
        name = request.form["name"],
        posts = posts
    )
    
    db.session.add(new_tag)
    db.session.commit()

    return redirect("/tags")

@app.route('/tags/<int:tag_id>')
def show_one_tag(tag_id):
    """Show listing of all posts with a specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)

# Need an Edit Tag route, both a GET to show the form and a POST to update the tag information
@app.route("/tags/<int:tag_id>/edit")
def show_edit_tag_form(tag_id):
    """Shows form to edit a tag"""

    tag=Tag.query.get_or_404(tag_id)

    return render_template("tags/edit.html", tag=tag)

@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def handle_edit_tag(tag_id):
    """Handles edit tag form submission"""

    tag=Tag.query.get_or_404(tag_id)
    tag.name = request.form["name"]

    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    """Handles deleting an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    
    return redirect("/tags")