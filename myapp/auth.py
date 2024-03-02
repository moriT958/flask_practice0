import functools

from flask import (
    Blueprint, flash, g, render_template, redirect, session, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from myapp.db import get_db


bp = Blueprint(name='auth', import_name=__name__, url_prefix='/auth')

# ユーザ登録のView
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # ユーザがフォームを送信した時,リクエストのメソッドはPOST
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # フォームが空でないか確認
        if not username:
            error = 'ユーザーネームを入力してください。'
        elif not password:
            error = 'パスワードを入力してください。'

        # フォームが入力されていたら、データベースに格納
        if error is None:
            try:
                db.execute(
                    "INSER INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = 'このユーザはすでに登録されています。'
            else:
                # 無事格納されたら、loginのViewに遷移
                return redirect(url_for('auth.login'))
            
        # エラーメッセージを表示
        flash(message=error)

    # ユーザからのリクエストがGETだった場合
    return render_template('auth/register.html')


# ユーザログイン用のView
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # データベースからユーザを取得
        user = db.execute(
            "SELECT * FROM user WHERE username = ?",
            username
        ).fetchone()  # fetchoneは一行返す、fetchallは全て返す
        if user is None:
            error = 'このユーザは登録されていません。'
        elif not check_password_hash(user['password'], password):
            error = 'このパスワードは不正です。'
        
        if error is None:
            # session(cookie)にデータを格納
            session.clear()
            session['user_id'] = user['id']
            redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')


# ユーザのログアウトView
@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    redirect(url_for('index'))


@bp.before_app_request  # View関数の前に実行されるように登録
def load_logedd_in_user():
    # sessionにユーザが格納されている場合、そのデータをgに保存
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?",
            user_id
        ).fetchone()


# decoratorを使用して、各Viewでログインチェックを行う
def login_required(view):
    
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            redirect(url_for('auth.login'))

        return view(**kwargs)

    # デコレートされた新しいViewを返す
    return wrapped_view