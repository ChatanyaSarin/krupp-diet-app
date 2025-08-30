# app.py
from flask import Flask
from flask_cors import CORS
from routes import bp

app = Flask(__name__)
app.url_map.strict_slashes = False  # <— accept both /auth/login and /auth/login/

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

app.register_blueprint(bp)

from routes import auth_login  # import the view function
app.add_url_rule("/auth/login", view_func=auth_login, methods=["POST"])

print("\n[FLASK ROUTES]")
for rule in app.url_map.iter_rules():
    print(f"  {','.join(sorted(rule.methods)):<18} {rule.rule}")
print()

if __name__ == "__main__":
    app.run(port=8000, debug=True)
