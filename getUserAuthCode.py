from flask import Flask, request, redirect
import subprocess
import time
import platform
from dotenv import load_dotenv, set_key
import os
from spotifywrapper import SpotifyWrapper
import requests

load_dotenv()

if (platform.system() == "Windows"):
    PLATFORM_BROWSER_OPEN = "explorer"
if (platform.system() == "Linux"):
    PLATFORM_BROWSER_OPEN = "xdg-open"

browser_process = None
# Start flask server
app = Flask("SpotiPy App")

@app.route("/")
def login():
    CLIENT_ID = os.getenv("CLIENT_ID")
    REDIRECT_URI = "http://localhost:8000/callback"
    SCOPES = "user-read-private user-read-email streaming user-read-playback-state playlist-read-private user-modify-playback-state user-top-read user-library-read"
    AUTH_URL = "https://accounts.spotify.com/authorize"

    auth_query_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": "someRandomState",
    }
    
    auth_url = f"{AUTH_URL}?{'&'.join([f'{key}={value}' for key, value in auth_query_params.items()])}"
    print(auth_url)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    # Retrieve the authorization code
    code = request.args.get("code")
    if not code:
        return "Authorization failed: No code received."
    else:
        # User API Token
        url = "https://accounts.spotify.com/api/token"

        # Headers and data payload
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv('CLIENT_SECRET'),
            "redirect_uri": "http://localhost:8000/callback",
            "code": code
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Check response status and content
        if response.status_code == 200:
            set_key(".env", "USER_REFRESH_KEY", response.json()['refresh_token'])
        else:
            print("Failed to fetch token:", response.status_code, response.text)
        return "ok"

process = subprocess.Popen([PLATFORM_BROWSER_OPEN, "http://127.0.0.1:8000"])  # Replace "xdg-open" with appropriate browser command for your OS
app.run(port=8000)