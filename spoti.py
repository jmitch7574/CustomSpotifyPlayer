import requests

class SpotiPy:
    def __init__(self, CLIENT_ID, CLIENT_SECRET):
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.API_KEY = None
        self.RefreshApiKey()

    def RefreshApiKey(self):
        # Spotify API endpoint
        url = "https://accounts.spotify.com/api/token"

        # Headers and data payload
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Check response status and content
        if response.status_code == 200:
            self.API_KEY = response.json()['access_token']
        else:
            print("Failed to fetch token:", response.status_code, response.text)
            self.API_KEY = None

    def GetArtistInfo(self, artistID):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/artists/" + artistID

        headers = {
            "Authorization": "Bearer " + self.API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            print("Failed to fetch artist: ", response.status_code, response.text)

    def GetPlaybackInfo(self):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/me"

        headers = {
            "Authorization": "Bearer " + self.API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            print("Failed to fetch me: ", response.status_code, response.text)