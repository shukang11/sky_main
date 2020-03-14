import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app import create_app

env: str = os.environ.get("FLASK_ENV") or "default"
print("runner.py " + env)
main_app = create_app(env)
# application = DispatcherMiddleware(main_app, {})
application = main_app

if __name__ == "__main__":
    application.run(host='localhost', port=9000, debug=True)