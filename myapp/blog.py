from flask import (
    url_for, render_template, redirect, flash, g, current_app, request, Blueprint
)

from werkzeug.exceptions import abort

from myapp.auth import login_required
from myapp.db import get_db

bp = Blueprint(name='blog', import_name=__name__)  
# url_prefixはデフォルトでindexとなるように__init__.pyで設定する


# blogのインデックスページにルーティング
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON u.id = p.author_id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


# postを作成するView
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'タイトルを入力してください。'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')


# idからpostを取得し、ログインユーザと作者が一致しているかチェック
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403, f"現在ログインしているユーザ({g.user['username']})では、この投稿は編集できません。")

    return post


# 投稿を編集するView
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'タイトルを入力してください。'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# 投稿を削除するView
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))