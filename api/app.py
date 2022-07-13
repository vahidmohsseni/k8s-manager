import os

from flask import Flask

from flask_app.controller import v1


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    
    # register the blueprints
    app.register_blueprint(v1.bp)


    return app


app = create_app()

if __name__ == '__main__':

    PORT = int(os.environ.get('PORT', 5001))
    HOST = 'localhost'
        
    app.run(host=HOST, port=PORT, debug=False)
