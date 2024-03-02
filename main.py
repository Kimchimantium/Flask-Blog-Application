from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import secrets, datetime

# Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()
secret_key = secrets.token_hex(16)

app = Flask(__name__)
app.config['SECRET_KEY'] = '16f1ba3f55e40b770f32403fbe96814b'
app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
ckeditor = CKEditor(app)

Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# time
now = datetime.datetime.now()
formatted_now = now.strftime('%B, %d, %Y')
# CONFIGURE TABLE


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# Get data as dict from sql
def get_post_db():
    with app.app_context():
        all_db = db.session.query(BlogPost).all()
    posts = []
    for data in all_db:
        posts.append({
            'id': data.id,
            'date': data.date,
            'title': data.title,
            'subtitle': data.subtitle,
            'author': data.author,
            'img_url': data.img_url,
            'body': data.body})
    return posts


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = get_post_db()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    posts = get_post_db()
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", index=index, post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["POST", "GET"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_db = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=formatted_now,
            author=form.author.data,
            body=form.body.data,
            img_url=form.img_url.data
        )
        db.session.add(new_db)
        db.session.commit()
        return redirect('/')
    return render_template('make-post.html', form=form)


@app.route('/edit-post/<int:index>', methods=["POST", "GET"])
def edit_post(index):
    # get post by index from sql db
    post_db = BlogPost.query.filter_by(id=index).first()
    form = CreatePostForm(obj=post_db)
    if form.validate_on_submit():
        form.populate_obj(post_db)
        db.session.commit()
        return redirect('/')
    pass
    return render_template('make-post.html', form=form)


@app.route('/delete/<int:index>', methods=["GET", "POST"])
def delete(index):
    if True:
        to_delete = db.session.query(BlogPost).filter_by(id=index).first()
        db.session.delete(to_delete)
        db.session.commit()
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=8880)



