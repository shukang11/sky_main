import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app import create_app

main_app = create_app(os.environ.get('FLASK_ENV') or 'default')
application = DispatcherMiddleware(main_app, {})

if __name__ == "__main__":
    main_app.run(port=9000)