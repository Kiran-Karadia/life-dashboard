from requests import Request, Response, get, post
import base64

BASE_ENDPOINT = "https://accounts.spotify.com"
CLIENT_ID = "715ce3e1c15349e189c2d999b7abfa48"
CLIENT_SECRET = "0d14d2ca2f1e40dfac3c602868e96baa"
REDIRECT_URL = "http://localhost:5000/callback"



class SpotifyAuth():
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.auth_header = f"Basic {base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()}"
        
    def generate_request_user_auth_url(self):
        query_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URL,
        "state": "QWERTY",
        "scope": "user-read-playback-state"
    }
        url = Request(
            method="GET",
            url=f"{BASE_ENDPOINT}/authorize",
            params=query_params
        ).prepare().url

        return url
    
    def get_access_token(self, auth_code):
        token_request = post(
            url=f"{BASE_ENDPOINT}/api/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": REDIRECT_URL
            },
            headers={
                "Authorization": self.auth_header,
                "content-type": "application/x-www-form-urlencoded"
            }
        )
        response = token_request.json()

        self.extract_tokens(response)
    
    def refresh_access_token(self):
        refresh_token_request = post(
            url=f"{BASE_ENDPOINT}/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            },
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "Authorization": self.auth_header
            }
        )

        response = refresh_token_request.json()

        self.extract_tokens(response)

    def extract_tokens(self, response_json):
        self.access_token = response_json["access_token"]
        self.refresh_token = response_json["refresh_token"]







