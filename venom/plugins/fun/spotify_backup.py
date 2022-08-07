# spotify.py

import spotipy
import os
import requests
import json
import base64
from PIL import Image

from venom import venom, Config, MyMessage, Collection

C_ID="a8eeb90ba695476e9db2c67f289f96e5"
C_SECRET="7ecbac43bed54eaa8f2e1c557aee8757"


CHANNEL = venom.getCLogger(__name__)


@venom.trigger('spot_auth')
async def spotify_auth(_, message: MyMessage):
    " authorise using client id and secret "
    if Config.HEROKU_ENV:
        return await message.edit("`Heroku app found, aborting...`", del_in=3)
    response = await message.ask("You're generating new token, are you sure? Reply '`y`' to continue.")
    if response.text.upper() != "Y":
        return await response.reply("`Process aborted.`")
    try:
        token = spotipy.util.prompt_for_user_token(None, scope="user-read-currently-playing", client_id=C_ID, client_secret=C_SECRET, redirect_uri="http://localhost:8888/callback")
    except Exception as e:
        return await message.edit(e)
    await Collection.SPOTIFY_TOKEN.update_one(
        {'_id': 'SPOTIFY_TOKEN'}, {'$set': {'token': token}}, upsert=True
    )
    await message.edit("<b>Spotify token generated.</b>", del_in=3)
    await CHANNEL.log(f"<b>Spotify token generated.</b>\n<b>TOKEN:</b> `{token}`")


""" @venom.trigger('spotnow')
async def spot_dl(_, message: MyMessage):
    " download from spotify "
    current_ = spot.currently_playing()
    artist = current_['item']['artists'][0]['name']
    song = current_['item']['name']
    if current_['item']['album']['images']:
        thumb = current_['item']['album']['images'][0]['url']
    else:
        album_entity = spot.search(f"album:{current_['item']['album']['name']}", type="album")
        album = spot.album()
        thumb = album_entity['albums']['items'][0]['images'][0]['url']
    await message.reply_photo(thumb, caption=f"<b>Artist:</b> {artist}\n<b>Song:</b> {song}") """

