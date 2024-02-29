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

    app = Flask(import_name=__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'data.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile(filename='config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return "<h1>Hello!</h1>"
    
    return app