import requests
import base64

class SpotiPy:
    def __init__(self, CLIENT_ID, CLIENT_SECRET, USER_REFRESH_KEY):
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.API_KEY = None
        self.USER_KEY = None
        self.USER_REFRESH_KEY = USER_REFRESH_KEY

        self.RefreshApiKeys()

    def RefreshApiKeys(self):
        # Spotify API endpoint
        url = "https://accounts.spotify.com/api/token"

        # Headers and data payload
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Check response status and content
        if response.status_code == 200:
            print("API Key refreshed")
            self.API_KEY = response.json()['access_token']
        else:
            print("Failed to refresh API Key:", response.status_code, response.text)
            self.API_KEY = None
        
        base64code = base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode()).decode()

        # Headers and data payload
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64code}"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.USER_REFRESH_KEY,
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=data)

        # Check response status and content
        if response.status_code == 200:
            print("User Key refreshed")
            self.USER_KEY = response.json()['access_token']
        else:
            print("Failed to refresh User Key:", response.status_code, response.text)
            print(response.json())

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

    def GetUserInfo(self):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/me"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            print("Failed to fetch me: ", response.status_code, response.text)

    
    def GetUserPlaybackInfo(self):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/me/player"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY
        }

        data = {
            "market": "GB"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            print("User not listening")
        if response.status_code == 402:
            print("User not listening")
        else:
            print("Failed to fetch me: ", response.status_code, response.text)

    def GetUserPlaylists(self):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/me/playlists?limit=5"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        if response.status_code == 402:
            print("User not listening")
            return None
        else:
            print("Failed to fetch me: ", response.status_code, response.text)

    def PlayItem(self, item):
        if (self.API_KEY == None):
            return
        
        print(item)
        
        url = "https://api.spotify.com/v1/me/player/play"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
            "Content-Type": "application/json"
        }

        data =  "{" + f"\"context_uri\":  \"{item}\"" + "}"

        response = requests.put(url, headers=headers, data=data)

        if response.status_code == 204:
            return
        if response.status_code == 402:
            print("User not listening")
        else:
            print("Failed to play music: ", response.status_code, response.text)

    def GetPlayListInfo(self, id):
        if (self.API_KEY == None):
            return
        
        url = f"https://api.spotify.com/v1/playlists/{id}"

        headers = {
            "Authorization": "Bearer " + self.API_KEY,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to get playlist: ", response.status_code, response.text)
