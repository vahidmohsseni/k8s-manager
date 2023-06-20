import os
from utils import logger
from flask import Flask
from waitress import serve
from routes import routes

ENV = os.environ.get("ENV")

app = Flask(__name__)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5002))
    HOST = os.environ.get("HOST", "localhost")
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", ".uploads")

    if not (HOST):
        raise Exception("No host defined")
    if not (PORT):
        raise Exception("No port defined")

    logger.info(f"Creating upload directory in {UPLOAD_DIR}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.register_blueprint(routes)
    if ENV == "prod":
        logger.info("Serving in production mode")
        serve(app, host=HOST, port=PORT)
    else:
        app.run(host=HOST, port=PORT)
