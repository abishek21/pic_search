from flask import Flask
from flask_caching import Cache
import redis
from rq import Queue

app = Flask(__name__)
app.config.from_object('config.Config')

cache = Cache(app)

r = redis.Redis(host='redis',
                port=6379)
q = Queue(connection=r)

def create_app():



    cache.init_app(app)

    with app.app_context():
        # Import and register routes
        from .routes import index_route, search_api_route,search_route,upload_api_route,upload_route

    return app
