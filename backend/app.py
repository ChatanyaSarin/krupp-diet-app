# app.py
from flask import Flask
from flask_cors import CORS
from routes import bp

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
