from flask import Flask
import os

# import the blueprints so other files can work...
from routes import routes
from auth import auth

app = Flask(__name__)
# 'imports' the flask code in this file and makes it as though it is a separate entitity,
# without having to deal with the consequences of simply using 'import' like we normally
# do in normal python
app.register_blueprint(routes)
app.register_blueprint(auth)

# If file is being run as "main", then do this
if __name__ == '__main__':
    alloc_port = os.environ['CS1999_PORT']
    os.environ['FLASK_ENV'] = 'development'  # HARD CODE since default is production
    app.run(debug=True, host="0.0.0.0", port=alloc_port)