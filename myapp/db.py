'''
データベースを操作する関数を定義
'''
import sqlite3

import click
from flask import g, current_app
'''
g: リクエストごとに作成される、データベースへの接続を保持するコンテキスト
current_app: リクエストを処理中のappを指し示す
'''


def get_db():
    if 'db' not in g:
        # sqlite3.connectは、app.configで設定したデータベースへのconnectionを作成する。
        g.db = sqlite3.connect(
            database=current_app.config['DATABASE'],
            detect_types=True
        )
        # sqlite3.Rowは、dictのように振る舞う行を返すようにconnectionへ伝える。
        g.db.row_factory = sqlite3.Row
    
    return g.db


def close_db(e=None):
    db = g.pop(name='db', default=None)

    # もし、dbへのconnectionが存在したら
    if db is not None:
        db.close()


# データベースを初期化する関数
def init_db():
    db = get_db()

    with current_app.open_resource(resource='schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# データベース初期化関数をコマンドから実行できるようにする
@click.command('init-db')
def init_db_command():
    init_db()
    click.echo(message='Initialized the Database.')


# close_dbとinit_db_command関数をappインスタンスに登録
def init_app(app):
    # レスポンスを返した後のクリーンアップを行う際、close_dbを呼び出すよう、Flaskへ伝える
    app.teardown_appcontext(close_db)
    # init_dbのコマンドを登録
    app.cli.add_command(init_db_command)