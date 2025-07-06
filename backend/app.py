from flask import Flask
from routes import bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
