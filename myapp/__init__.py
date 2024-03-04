'''
このファイルは、次の二つの役割を果たす
1. my-appをパッケージとして扱う
2. Application Factoryを持つ
'''

import os

from flask import Flask


# Application Factoryとなる関数
# アプリの設定や登録はこの関数内で行う
def create_app(test_config=None):

    # appのインスタンスを作成
    app = Flask(import_name=__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'data.sqlite')
    )

    # 引数に設定オブジェクトがなければ、ファイルから読み込む
    if test_config is None:
        app.config.from_pyfile(filename='config.py', silent=True)
    # あったら、それを読む
    else:
        app.config.from_mapping(test_config)

    # インスタンスパスが存在することを確立
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # appに、db操作を登録
    from . import db
    db.init_app(app)

    # authのBlueprintをアプリに登録
    from . import auth
    app.register_blueprint(auth.bp)

    # blogのBlueprintをアプリに登録
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule(rule='/', endpoint='index')
    
    return app