# client.py

import logging
import asyncio

from pyrogram import Client

from venom import Config


async def _init_tasks():
    if not Config._INIT:
        return
    await asyncio.gather(*Config._INIT)
    Config._INIT.clear()


class Venom(Client):
    def __init__(self):
        kwargs = {
            'name': 'VenomX',
            'api_id': Config.API_ID,
            'api_hash': Config.API_HASH,
            'plugins': dict(root='venom')
        }
        if Config.STRING_SESSION and Config.BOT_TOKEN:
            kwargs['session_string'] = Config.STRING_SESSION
            kwargs['bot_token'] = Config.BOT_TOKEN
        elif Config.BOT_TOKEN:
            kwargs['in_memory'] = True
            kwargs['bot_token'] = Config.BOT_TOKEN
        else:
            logging.error("!!! BOT_TOKEN required. !!!")
        super().__init__(**kwargs)

    async def start(self):
        await super().start()

    async def stop(self):
        await super().stop()

    async def restart(self):
        await super().restart()

    async def sleep(self, msg):
        await msg.reply("`Sleeping for (10) Seconds.`")