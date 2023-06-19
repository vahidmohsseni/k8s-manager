import os
from flask import Flask

from routes import routes


app = Flask(__name__)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5002))
    HOST = os.environ.get("HOST", "localhost")

    if not (HOST):
        raise Exception("No host defined")
    if not (PORT):
        raise Exception("No port defined")

    app.register_blueprint(routes)
    print(app.url_map)
    app.run(host=HOST, port=PORT)
