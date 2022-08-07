# spotify.py

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from venom import venom, Config, MyMessage, Collection, logging

C_ID="795ff76665bc48f29a617fdf1ccb92f6"
C_SECRET="85c7b878cf714a5a84d6ce71c193fe62"

CHANNEL = venom.getCLogger(__name__)


@venom.trigger('spotnow')
async def spot_dl(_, message: MyMessage):
    " download from spotify "
    client_id = C_ID
    client_secret = C_SECRET
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spot = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    current_ = spot.currently_playing(market=91)
    await message.edit(current_)