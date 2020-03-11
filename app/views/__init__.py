from flask import Blueprint, Flask

def init_app(app: Flask):
    from ..views import user
    from ..views import todo
    from ..views import rss
    from ..views import dashboard
    from ..views import file as f
    
    app.register_blueprint(user.api, url_prefix='/user')
    app.register_blueprint(todo.api, url_prefix='/todo')
    app.register_blueprint(rss.api, url_prefix='/rss')
    app.register_blueprint(dashboard.api, url_prefix='/dashboard')
    app.register_blueprint(f.api, url_prefix='/storage')