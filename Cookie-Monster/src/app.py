from flask import Flask, request, make_response, render_template_string
import base64, json, os

app = Flask(__name__)

FLAG = open("/flag.txt").read().strip()

STYLE = """
body { background: #0a0a0a; color: #c0c0c0; font-family: 'Courier New', monospace; padding: 40px; max-width: 600px; margin: auto; }
h1 { color: #ff6600; }
.flag { background: #1a1a2e; border: 2px solid #ff6600; padding: 20px; border-radius: 8px; color: #00ff88; font-size: 1.2em; }
form { margin: 20px 0; }
input, button { background: #111; color: #ff6600; border: 1px solid #ff6600; padding: 10px 15px; font-family: monospace; font-size: 1em; }
button:hover { background: #ff6600; color: #0a0a0a; cursor: pointer; }
.info { color: #666; font-size: 0.9em; }
"""

LOGIN_PAGE = """
<!DOCTYPE html><html><head><title>SKL Corp - Login</title><style>{{ style }}</style></head>
<body>
<h1>🍪 SKL Corp - Portail</h1>
<p>Connectez-vous pour accéder au système.</p>
<form method="POST">
    <input type="text" name="username" placeholder="Identifiant"><br><br>
    <input type="password" name="password" placeholder="Mot de passe"><br><br>
    <button type="submit">Connexion</button>
</form>
<p class="info">Compte invité : guest / guest</p>
</body></html>
"""

DASHBOARD = """
<!DOCTYPE html><html><head><title>SKL Corp - Dashboard</title><style>{{ style }}</style></head>
<body>
<h1>🍪 SKL Corp - Dashboard</h1>
<p>Bienvenue, <strong>{{ username }}</strong> !</p>
{% if is_admin %}
<div class="flag">🏁 Flag : {{ flag }}</div>
{% else %}
<p>Vous êtes connecté en tant qu'utilisateur standard.</p>
<p class="info">Seul l'administrateur peut voir le flag.</p>
{% endif %}
</body></html>
"""

def make_cookie(data):
    return base64.b64encode(json.dumps(data).encode()).decode()

def read_cookie(value):
    try:
        return json.loads(base64.b64decode(value))
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "guest" and password == "guest":
            resp = make_response(render_template_string(DASHBOARD, style=STYLE, username=username, is_admin=False, flag=FLAG))
            resp.set_cookie("session", make_cookie({"username": username, "role": "user"}))
            return resp
        return render_template_string(LOGIN_PAGE, style=STYLE)

    cookie = request.cookies.get("session")
    if cookie:
        data = read_cookie(cookie)
        if data and "username" in data:
            is_admin = data.get("role") == "admin"
            return render_template_string(DASHBOARD, style=STYLE, username=data["username"], is_admin=is_admin, flag=FLAG)

    return render_template_string(LOGIN_PAGE, style=STYLE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
