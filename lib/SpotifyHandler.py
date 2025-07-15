import logging, os, requests
from dotenv import load_dotenv

class SpotifyHandler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Load environment variables
        load_dotenv()
        self.client_id     = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.refresh_token = os.getenv('SPOTIFY_REFRESH_TOKEN')

        self.logger.info('Initialized SpotifyHandler.')

    def get_currently_playing(self):
        url = 'https://api.spotify.com/v1/me/player/currently-playing'
        headers = {
            "Accept": "application/j    son",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.refresh_access_token()}"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 204:
                response.raise_for_status()
                spotify_data = response.json()
                data = {
                    'song_name': spotify_data['item']['name'],
                    'album_name': spotify_data['item']['album']['name'],
                    'artist_name': spotify_data['item']['artists'][0]['name'],
                    'album_art_url': spotify_data['item']['album']['images'][1]['url'], # Use the medium sized image
                    'item_id': spotify_data['item']['id'],
                    'is_playing': spotify_data['is_playing']
                }

                return data
            # return response.json()
            else:
                self.logger.info('No content returned from Spotify API.')
        except Exception as e:
            self.logger.error(f'Exception occurred while making request to {url}: {repr(e)}')

        return None


    def refresh_access_token(self):
        self.logger.info('Refreshing Spotify access token.')
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            self.logger.error(f'Exception occurred while refreshing Spotify access token: {repr(e)}')


    def __get_refresh_token(self, authorization_code):
        # Used this a while ago to get the refresh token. Could be useful later if the
        # refresh token is revoked
        response = requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "https://tars.requestcatcher.com/",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        return response.json()
