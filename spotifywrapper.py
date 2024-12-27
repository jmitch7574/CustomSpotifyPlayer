import requests
import base64

class SpotifyWrapper:
    def __init__(self, CLIENT_ID, CLIENT_SECRET, USER_REFRESH_KEY):
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.API_KEY = None
        self.USER_KEY = None
        self.USER_REFRESH_KEY = USER_REFRESH_KEY
        self.LAST_PLAYBACK_INFO = {}
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
            return response.json()
        else:
            print("Failed to fetch artist: ", response.status_code, response.text)


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
    
    
    def GetAlbumInfo(self, id):
        if (self.API_KEY == None):
            return
        
        url = f"https://api.spotify.com/v1/albums/{id}"

        headers = {
            "Authorization": "Bearer " + self.API_KEY,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to get album: ", response.status_code, response.text)

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
            self.LAST_PLAYBACK_INFO = response.json()
            return response.json()
        elif response.status_code == 204:
            print("User not listening")
        if response.status_code == 402:
            print("User not listening")
        else:
            print("Failed to fetch me: ", response.status_code, response.text)
        self.LAST_PLAYBACK_INFO = None

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

    
    def GetUserAlbums(self):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/me/albums?limit=5"

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


    def GetUserArtists(self):
        if (self.API_KEY == None):
            return
        
        url = "https://api.spotify.com/v1/me/top/artists?limit=5&time_range=short_term"
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
            print("Failed to fetch top artists: ", response.status_code, response.text)


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

    def SkipToNextSong(self):
        if (self.API_KEY == None):
            return
        
        url = f"https://api.spotify.com/v1/me/player/next"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            return 
        else:
            print("Failed to skip: ", response.status_code, response.text)

    def PreviousSong(self):
        if (self.API_KEY == None):
            return
        
        url = f"https://api.spotify.com/v1/me/player/previous"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            return 
        else:
            print("Failed to previous song: ", response.status_code, response.text)

    def SeekSong(self, ms):
        if (self.API_KEY == None):
            return
        
        url = f"https://api.spotify.com/v1/me/player/seek?position_ms={ms}"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.put(url, headers=headers)

        if response.status_code == 200:
            return 
        else:
            print("Failed to seek: ", response.status_code, response.text)


    def RestartSong(self):
        self.SeekSong(0)

    def PreviousButtonPressed(self):
        if not self.LAST_PLAYBACK_INFO.get('progress_ms'):
            print("User not playing")
            return
        if int(self.LAST_PLAYBACK_INFO.get('progress_ms')) > 3000:
            self.RestartSong()
        else:
            self.PreviousSong()

    def Pause(self):
        if (self.API_KEY == None):
            return
        
        url = f"https://api.spotify.com/v1/me/player/pause"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.put(url, headers=headers)

        if response.status_code == 200:
            return 
        else:
            print("Failed to seek: ", response.status_code, response.text)

    def Resume(self):
        if (self.API_KEY == None):
            return
        if not self.LAST_PLAYBACK_INFO:
            print("User not playing")
            return
        
        url = "https://api.spotify.com/v1/me/player/play"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.put(url, headers=headers)

        if response.status_code == 200:
            return
        if response.status_code == 402:
            print("User not listening")
        else:
            print("Failed to play music: ", response.status_code, response.text)

    def pause_button_pressed(self):
        if 'is_playing' not in self.LAST_PLAYBACK_INFO.keys():
            print("User not lsitening")
            return
        if self.LAST_PLAYBACK_INFO.get('is_playing') == True:
            self.Pause()
        else:
            self.Resume()

    def toggle_shuffle(self):
        if(self.API_KEY == None):
            return
        if not self.LAST_PLAYBACK_INFO:
            return
        
        state = not self.LAST_PLAYBACK_INFO.get('shuffle_state')
        
        url = f"https://api.spotify.com/v1/me/player/shuffle?state={state}"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.put(url, headers=headers)

        if response.status_code == 200:
            return
        if response.status_code == 402:
            print("User not listening")
        else:
            print("Failed to toggle shuffle: ", response.status_code, response.text)

    def toggle_repeat(self):
        if(self.API_KEY == None):
            return
        if not self.LAST_PLAYBACK_INFO:
            return
        
        last_state = self.LAST_PLAYBACK_INFO.get("repeat_state")
        state = ""

        if last_state == 'off':
            state = 'context'
        elif last_state == 'context':
            state = 'track'
        else:
            state = 'off'
        
        url = f"https://api.spotify.com/v1/me/player/repeat?state={state}"

        headers = {
            "Authorization": "Bearer " + self.USER_KEY,
        }

        response = requests.put(url, headers=headers)

        if response.status_code == 200:
            return
        if response.status_code == 402:
            print("User not listening")
        else:
            print("Failed to toggle repeat: ", response.status_code, response.text)

