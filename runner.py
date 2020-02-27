import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask_script import Manager
from flask_migrate import MigrateCommand
from app import create_app

env: str = os.environ.get("FLASK_ENV") or "default"
main_app = create_app(env)
# application = DispatcherMiddleware(main_app, {})
application = main_app

manager = Manager(main_app)
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()
