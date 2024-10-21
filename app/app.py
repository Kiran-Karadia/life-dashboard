import base64
import datetime
from requests import Request, Response, get, post, put
from flask import Flask, request, abort, render_template, redirect, session
from markupsafe import escape
import os
from dotenv import load_dotenv


load_dotenv()
BASE_ENDPOINT = "https://accounts.spotify.com"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = "http://localhost:5000/callback"
BASE_API = "https://api.spotify.com"
app = Flask(__name__)
app.secret_key = b"kiran"

def request_user_auth():
    query_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URL,
        "state": "QWERTY",
        "scope": "user-read-playback-state user-modify-playback-state"
         
    }
    url = Request(
        method="GET",
        url=f"{BASE_ENDPOINT}/authorize",
        params=query_params
    ).prepare().url

    return url

def get_token(auth_code):
    request = post(
        url=f"{BASE_ENDPOINT}/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URL
        },
        headers={
            "Authorization": encode_auth(),
            "content-type": "application/x-www-form-urlencoded"
        }
    )

    return request.json()

def get_playback_state():
    if session["username"] == "Kiran":
        return "You're not authenticated!"
    
    token = session['token']
    
    request = get(
        url=f"{BASE_API}/v1/me/player",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    if request.status_code == 200:
        return request.json()
    else:
        return f"Error has status code {request.status_code}. The reason is: {request.reason}"
    
def start_resume_playback(token):
    request = put(
        url=f"{BASE_API}/v1/me/player/play",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "postion_ms": 0
        }
    )
    
    if request.status_code == 204:
        return None
    elif request.status_code == 403:
        pause_playback(token)
        return render_template("all_functions.html")
    else:
        return f"Error has status code {request.status_code}. The reason is: {request.json()["error"]}"
    
def pause_playback(token):
    request = put(
        url=f"{BASE_API}/v1/me/player/pause",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )
    
    if request.status_code == 204:
        return render_template("all_functions.html")
    else:
        render_template("all_functions.html")
        return f"Error has status code {request.status_code}. The reason is: {request.reason}"

def refersh_access_token(refresh_token):
    request = post(
        url=f"{BASE_ENDPOINT}/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        headers={
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": encode_auth()
        }
    )

    return request.json()

def encode_auth():
    return f"Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}"


class Auth:
    def __init__(self):
        self.token = None

    def set_token(self, token, refresh_token):
        self.token = token
        self.refresh_token = refresh_token

auth = Auth()

@app.route("/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    state = request.args.get("state")

    auth_json = get_token(code)
    access_token = auth_json["access_token"]
    refresh_token = auth_json["refresh_token"]

    auth.set_token(access_token, refresh_token)
    
    session['token'] = access_token
    session['refresh_token'] = refresh_token
    
    return redirect('home')


@app.route("/")
@app.route("/home")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
    session['username'] = "Kiran"
    return redirect(request_user_auth())

@app.route("/capitalise/<word>")
def capitalise(word: str):
    return escape(word).upper()

@app.route("/add/<int:n1>/<int:n2>")
def sum(n1, n2):
    return f"When you add {n1} and {n2}, you get {n1 + n2}"

@app.route("/users/<int:user_id>")
def greet_user(user_id):
    all_users = ["Kiran", "Lucy", "Vince", "Leo"]
    try:
        return "<h2>{}</h2>".format(f"Hi there {all_users[user_id]}!")
    except Exception as error:
        abort(404, error)

@app.route("/time")
def time():
    return render_template("index.html", utc_dt=(datetime.datetime.now()))

@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        if request.form["action"] == "Get current playback":
            return get_playback_state()
        elif request.form["action"] == "Get devices":
            return start_resume_playback(auth.token)
            
    
    return render_template("all_functions.html")

